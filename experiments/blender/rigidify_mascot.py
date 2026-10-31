"""Turn a Meshy/Mixamo-rigged GLB into a Lego-style minifigure rig, and render checks.

blender -b -P rigidify.py -- <in.glb> <out_dir> <name> <mode: soft|lego>

lego mode:
- every vertex is bound 100% to one bone (no soft bending): head, torso+hips, upper arm,
  forearm, hand, and each leg as ONE piece (hip to toe);
- in every action the legs only swing forward/back: the hip-to-foot direction from the
  original animation is kept in the side view and its sideways part is dropped, so the
  retargeted human hip roll and knee bend no longer bow the short Lego legs.
"""
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

src, out_dir, name, mode = sys.argv[-4], Path(sys.argv[-3]), sys.argv[-2], sys.argv[-1]
out_dir.mkdir(parents=True, exist_ok=True)
P = "mixamorig:"
HAIRLOCK = os.environ.get("HAIRLOCK") == "1"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o)
mesh = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
scene = bpy.context.scene
arm.animation_data_create()

PARTS = {
    "Head": ["Neck", "Head", "HeadTop_End", "headfront"],
    "Spine2": ["Hips", "Spine", "Spine1", "Spine2", "LeftShoulder", "RightShoulder"],
}
for s in ("Left", "Right"):
    PARTS[s + "Arm"] = [s + "Arm"]
    PARTS[s + "ForeArm"] = [s + "ForeArm"]
    PARTS[s + "Hand"] = [s + "Hand", s + "HandMiddle4"]
    PARTS[s + "UpLeg"] = [s + "UpLeg", s + "Leg", s + "Foot", s + "ToeBase", s + "Toe_End"]


def full(b):
    return b if b == "headfront" else P + b


def rigid_weights():
    part_of = {}
    for part, bones in PARTS.items():
        for b in bones:
            g = mesh.vertex_groups.get(full(b))
            if g:
                part_of[g.index] = part
    # rest-pose landmarks (world space, Z up)
    bw = {b.name: arm.matrix_world @ b.head_local for b in arm.data.bones}
    torso_half = 0.85 * min(abs(bw[P + "LeftArm"].x), abs(bw[P + "RightArm"].x))
    hip_z, neck_z = bw[P + "LeftUpLeg"].z, bw[P + "Neck"].z
    hem = 0.08 * (neck_z - bw[P + "LeftFoot"].z)
    choice = []
    for v in mesh.data.vertices:
        score = {}
        for ge in v.groups:
            part = part_of.get(ge.group)
            if part:
                score[part] = score.get(part, 0.0) + ge.weight
        part = max(score, key=score.get) if score else None
        w = mesh.matrix_world @ v.co
        in_torso = abs(w.x) < torso_half and hip_z < w.z < neck_z
        # everything inside the torso box is the torso piece (keeps the chest print whole)
        if part and part != "Spine2" and "UpLeg" not in part and in_torso:
            part = "Spine2"
        # a sweater/jacket hem that hangs just below the hip joint stays on the torso,
        # otherwise the swinging leg drags it along
        elif part and "UpLeg" in part and abs(w.x) < torso_half and w.z > hip_z - hem:
            part = "Spine2"
        if HAIRLOCK and part:
            # long hair runs from the head past the shoulders: head, hair and torso are one piece,
            # so nothing tears at the neck; only clean arm skin (no head pull) swings
            if part == "Head" or ("UpLeg" not in part and score.get("Head", 0.0) > 0.0):
                part = "Spine2"
        elif part and part != "Head" and not in_torso and score.get("Head", 0.0) >= 0.1 and w.z > hip_z:
            part = "Head"
        choice.append(part)
    # hair strands below the head: soft blend to a sway bone, 0 at the scalp, 1 at the tips
    hair = {}
    if HAIRLOCK:
        head_groups = {mesh.vertex_groups[full(b)].index for b in PARTS["Head"] if mesh.vertex_groups.get(full(b))}
        cand = {}
        for i, v in enumerate(mesh.data.vertices):
            w = mesh.matrix_world @ v.co
            if choice[i] == "Spine2" and w.z < neck_z and abs(w.x) >= 0.6 * torso_half and any(
                    ge.group in head_groups and ge.weight > 0.0 for ge in v.groups):
                cand[i] = w.z
        if cand:
            tip_z = min(cand.values())
            for i, z in cand.items():
                hair[i] = min(1.0, (neck_z - z) / max(neck_z - tip_z, 1e-4)) ** 1.5
    targets = {p: mesh.vertex_groups.get(full(p)) or mesh.vertex_groups.new(name=full(p)) for p in PARTS}
    for g in list(mesh.vertex_groups):
        g.remove(range(len(mesh.data.vertices)))
    sway = mesh.vertex_groups.new(name="HairSway") if hair else None
    for i, part in enumerate(choice):
        if part:
            t = hair.get(i, 0.0)
            targets[part].add([i], 1.0 - t, "REPLACE")
            if t > 0.0:
                sway.add([i], t, "REPLACE")
    return bool(hair)


def add_hair_sway():
    """A bone at the head that swings the hair tips with the walk cycle."""
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    head = eb[P + "Head"]
    b = eb.new("HairSway")
    b.head = head.head.copy()
    b.tail = head.head + (head.tail - head.head).normalized() * 0.1
    b.parent = eb[P + "Spine2"]
    bpy.ops.object.mode_set(mode="OBJECT")
    pb = arm.pose.bones["HairSway"]
    pb.rotation_mode = "QUATERNION"
    for act in bpy.data.actions:
        arm.animation_data.action = act
        f0, f1 = int(act.frame_range[0]), int(math.ceil(act.frame_range[1]))
        period = max(f1 - f0, 1)
        for f in range(f0, f1 + 1, 2):
            ph = 2 * math.pi * (f - f0) / period
            # front/back flutter twice per cycle (each step), gentle side sway once per cycle
            e = (math.radians(7) * math.sin(2 * ph), 0.0, math.radians(5) * math.sin(ph + 0.6))
            pb.rotation_quaternion = Matrix.Rotation(e[0], 4, "X").to_quaternion() @ \
                Matrix.Rotation(e[2], 4, "Z").to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=f)


UPRIGHT = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"]


def upright(action):
    """A Lego torso does not bend: drop every hip/spine/neck/head rotation, keep the walk bob."""
    paths = {f'pose.bones["{P + b}"].rotation_quaternion' for b in UPRIGHT}
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in [fc for fc in bag.fcurves if fc.data_path in paths]:
                    bag.fcurves.remove(fc)
    for b in UPRIGHT:
        pb = arm.pose.bones.get(P + b)
        if pb:
            pb.rotation_quaternion = (1, 0, 0, 0)


def calm_arms(action, keep=0.5):
    """Halve the arm swing so arms stay beside the body instead of cutting through hair."""
    arm.animation_data.action = action
    f0, f1 = int(action.frame_range[0]), int(math.ceil(action.frame_range[1]))
    bones = [arm.pose.bones.get(P + s + b) for s in ("Left", "Right") for b in ("Arm", "ForeArm")]
    frames = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        frames[f] = [pb.rotation_quaternion.copy() for pb in bones if pb]
    ident = Matrix.Identity(3).to_quaternion()
    for f, quats in frames.items():
        for pb, q in zip([b for b in bones if b], quats):
            pb.rotation_quaternion = ident.slerp(q, keep)
            pb.keyframe_insert("rotation_quaternion", frame=f)


def lego_legs(action):
    arm.animation_data.action = action
    lat = (arm.matrix_world.inverted().to_3x3() @ Vector((1, 0, 0))).normalized()
    f0, f1 = (int(math.floor(x)) for x in action.frame_range)
    f1 = max(f1, int(math.ceil(action.frame_range[1])))
    targets = {}
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        for s in ("Left", "Right"):
            hip = arm.pose.bones[P + s + "UpLeg"].head
            foot = arm.pose.bones[P + s + "Foot"].head
            d = foot - hip
            targets[(f, s)] = d - d.dot(lat) * lat
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        for s in ("Left", "Right"):
            pb = arm.pose.bones[P + s + "UpLeg"]
            par = pb.parent
            base = par.matrix @ par.bone.matrix_local.inverted() @ pb.bone.matrix_local
            head = base.translation.copy()
            foot_rest = arm.data.bones[P + s + "Foot"].head_local
            rest_dir = (base @ pb.bone.matrix_local.inverted() @ foot_rest) - head
            a = rest_dir - rest_dir.dot(lat) * lat
            b = targets[(f, s)]
            ang = math.atan2(lat.dot(a.cross(b)), a.dot(b))
            rot = Matrix.Rotation(ang, 4, lat)
            pb.matrix = Matrix.Translation(head) @ rot @ Matrix.Translation(-head) @ base
            pb.keyframe_insert("rotation_quaternion", frame=f)
            for child in (s + "Leg", s + "Foot", s + "ToeBase"):
                c = arm.pose.bones.get(P + child)
                if c:
                    c.rotation_quaternion = (1, 0, 0, 0)
                    c.keyframe_insert("rotation_quaternion", frame=f)


for act in list(bpy.data.actions):
    if act.name.startswith("Running"):  # Sena: no running, walking/standing is enough
        bpy.data.actions.remove(act)

if mode == "lego":
    has_hair = rigid_weights()
    for act in list(bpy.data.actions):
        upright(act)
        calm_arms(act)
        lego_legs(act)
    if has_hair:
        add_hair_sway()
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=str(out_dir / f"{name}-lego.glb"), export_animations=True,
                              export_animation_mode="ACTIONS")

# full-body check renders
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scene.render.engine = eng
        break
    except TypeError:
        pass
scene.render.resolution_x, scene.render.resolution_y = 384, 512
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.14, 0.16, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.3
scene.world = world
bpy.ops.object.light_add(type="SUN", rotation=(0.8, 0.2, 0.4))
bpy.context.object.data.energy = 3
arm.animation_data.action = None
scene.frame_set(0)
zs = [(mesh.matrix_world @ Vector(c)).z for c in mesh.bound_box]
h = max(zs) - min(zs)
cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 1.35 * h
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
center = Vector((0, 0, min(zs) + 0.5 * h))
cam.location = center + Vector((0.6, -3.0, 0.25)) * h
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam
shots = [(a.name, int(a.frame_range[0] + k * (a.frame_range[1] - a.frame_range[0]) / 3))
         for a in bpy.data.actions for k in (0, 1, 2)]
for an, f in shots:
    arm.animation_data.action = bpy.data.actions[an]
    scene.frame_set(f)
    scene.render.filepath = str(out_dir / f"{name}-{mode}-{an}-{f:03d}.png")
    bpy.ops.render.render(write_still=True)
print("DONE", name, mode)
