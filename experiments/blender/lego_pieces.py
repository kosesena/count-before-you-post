"""Cut a single-shell Meshy minifigure into real Lego pieces and animate them.

blender -b -P lego_pieces.py -- <in.glb> <out.glb> <check_dir>

Pieces: body (head + hair + torso + hips), left/right arm, left/right leg.
Each piece is cut on clean planes/capsules, its open border is capped, and it is bound
100% to one bone of a small hand-built rig, so nothing can stretch between pieces.
Hair tips get a soft sway bone. Actions: Walk, Idle, Wave.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

src, split_src, dst, check = sys.argv[-4], sys.argv[-3], sys.argv[-2], Path(sys.argv[-1])
check.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type != "MESH"]:
    bpy.data.objects.remove(o)
mesh = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
bpy.context.view_layer.objects.active = mesh
mesh.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ---- Meshy part labels: 0 hair, 1 torso+arms, 2 hips+legs, 3 face (different scale) ----
from mathutils.kdtree import KDTree
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=split_src)
parts = sorted([o for o in bpy.data.objects if o not in before and o.type == "MESH"], key=lambda o: o.name)
pts = [(o.matrix_world @ v.co, i) for i, o in enumerate(parts) for v in o.data.vertices]
for o in list(bpy.data.objects):
    if o not in before:
        bpy.data.objects.remove(o)
def bbox(cs):
    return [min(c[k] for c in cs) for k in range(3)], [max(c[k] for c in cs) for k in range(3)]
smin, smax = bbox([p for p, _ in pts])
mmin, mmax = bbox([v.co for v in mesh.data.vertices])
def to_mesh(p, flip_y):
    out = []
    for k in range(3):
        t = (p[k] - smin[k]) / (smax[k] - smin[k])
        if k == 1 and flip_y:
            t = 1 - t
        out.append(mmin[k] + t * (mmax[k] - mmin[k]))
    return Vector(out)
best = None
for flip in (False, True):
    kd = KDTree(len(pts))
    for j, (p, _) in enumerate(pts):
        kd.insert(to_mesh(p, flip), j)
    kd.balance()
    err = sum(kd.find(mesh.data.vertices[i].co)[2] for i in range(0, len(mesh.data.vertices), 997))
    if best is None or err < best[0]:
        best = (err, kd, flip)
_, kd, flipped = best
print("SPLIT flip_y", flipped)
label = [pts[kd.find(v.co)[1]][1] for v in mesh.data.vertices]

# ---- landmarks, measured on the figure (front faces -Y, up is +Z) ----
cos = [v.co for v in mesh.data.vertices]
zmin, zmax = min(c.z for c in cos), max(c.z for c in cos)
H = zmax - zmin
z0 = zmin
# centre line = middle of the gap between the shins (floor props and hair don't reach there)
shins = sorted(c.x for c in cos if z0 + 0.08 * H < c.z < z0 + 0.18 * H)
mid = shins[len(shins) // 2]
gaps = [(b - a, (a + b) / 2) for a, b in zip(shins, shins[1:]) if abs((a + b) / 2 - mid) < 0.12 * H]
cx = max(gaps)[1] if gaps and max(gaps)[0] > 0.004 * H else mid
by_part = {}
for c, l in zip(cos, label):
    by_part.setdefault(l, []).append(c)
# Meshy's part order and count differ per figure, so give each part a role by where it sits
LEGS = min(by_part, key=lambda l: min(c.z for c in by_part[l]))
def core_count(l):
    return sum(1 for c in by_part[l] if abs(c.x - cx) < 0.06 * H and z0 + 0.4 * H < c.z < z0 + 0.55 * H)
TORSO = max((l for l in by_part if max(c.z for c in by_part[l]) < z0 + 0.85 * H or l == LEGS),
            key=core_count)  # hair and heads reach the top, the torso never does
neck_top = min(max(c.z for c in by_part[TORSO]), z0 + 0.68 * H)
legs_top = max(c.z for c in by_part[LEGS])
hips_top = legs_top if LEGS != TORSO and legs_top < neck_top - 0.1 * H else z0 + 0.52 * (neck_top - z0)
lower = [c for c in by_part[LEGS] + (by_part[TORSO] if TORSO != LEGS else []) if c.z < hips_top]
# Lego legs turn at the hip axle, a little over half way up the hips+legs block
hip_cut = z0 + 0.58 * (hips_top - z0)
# hip half-width = outer edge of the thighs (hands never hang that low)
thigh = sorted(abs(c.x - cx) for c in lower if hip_cut - 0.07 * H < c.z < hip_cut - 0.02 * H and abs(c.x - cx) < 0.35 * H)
bot_hw = thigh[int(0.98 * (len(thigh) - 1))] if thigh else 0.15 * H
L = dict(
    torso_bot_z=hips_top - z0, torso_top_z=neck_top - 0.06 * H - z0,
    torso_bot_hw=bot_hw, torso_top_hw=0.75 * bot_hw,
    shoulder_z=neck_top - 0.06 * H - z0,
    shoulder_x=0.75 * bot_hw + 0.02 * H,
    arm_y=sum(c.y for c in by_part[TORSO]) / len(by_part[TORSO]),
)
role = {}
for l, cs in by_part.items():
    if l in (LEGS, TORSO):
        continue
    cen = sum(cs, Vector()) / len(cs)
    top = max(c.z for c in cs)
    if top > z0 + 0.7 * H:
        role[l] = "Hair"  # hair, face, hats: ride on the body, tips may sway
    elif cen.z > hip_cut and abs(cen.x - cx) > 0.75 * bot_hw:
        role[l] = "Arm" + ("R" if cen.x > cx else "L")  # something held in a hand
    else:
        role[l] = "Body"
HAIR = {l for l, r in role.items() if r == "Hair"}
print("ROLES legs", LEGS, "torso", TORSO, role)
print("LANDMARKS", {k: round(v / H, 3) for k, v in L.items()}, "cx", round(cx / H, 3), "hip_cut", round((hip_cut - z0) / H, 3))


def torso_hw(z):
    t = (z0 + L["torso_top_z"] - z) / (L["torso_top_z"] - L["torso_bot_z"])
    return L["torso_top_hw"] + max(0.0, min(1.0, t)) * (L["torso_bot_hw"] - L["torso_top_hw"])


def arm_axis(side):
    s = 1 if side == "R" else -1
    a = Vector((cx + s * L["shoulder_x"], L["arm_y"], z0 + L["shoulder_z"]))
    return a, a - Vector((0, 0, 0.1 * H))  # bone points up from the shoulder


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + t * ab)).length, t


def classify(p, lab):
    if lab in role:
        return "Body" if role[lab] == "Hair" else role[lab]
    if p.z < hip_cut and lab in (LEGS, TORSO) and abs(p.x - cx) < 1.3 * L["torso_bot_hw"]:
        return "LegR" if p.x > cx else "LegL"
    if lab == LEGS and lab != TORSO:
        return "Body"
    # torso + arms: everything outside the torso block is an arm (sleeve and C-hand)
    if abs(p.x - cx) > torso_hw(p.z) + 0.004 * H and p.z < z0 + L["shoulder_z"] + 0.03 * H:
        return "ArmR" if p.x > cx else "ArmL"
    return "Body"


PIECES = ["Body", "ArmL", "ArmR", "LegL", "LegR"]
bm = bmesh.new()
bm.from_mesh(mesh.data)
bm.verts.ensure_lookup_table()
fpart = bm.faces.layers.int.new("piece")
bm.verts.ensure_lookup_table()
vlab = bm.verts.layers.int.new("lab")
for v in bm.verts:
    v[vlab] = label[v.index]
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6 * H)
seam_open = {e for e in bm.edges if e.is_boundary}  # real openings in the scan, leave them
for f in bm.faces:
    labs = [v[vlab] for v in f.verts]
    f[fpart] = PIECES.index(classify(f.calc_center_median(), max(set(labs), key=labs.count)))
vlabel = {}
cut = [e for e in bm.edges if len({f[fpart] for f in e.link_faces}) > 1]
bmesh.ops.split_edges(bm, edges=cut)
# cap only the borders our cut opened, so each piece reads as solid plastic
borders = [e for e in bm.edges if e.is_boundary and e not in seam_open]
caps = bmesh.ops.holes_fill(bm, edges=borders, sides=0)["faces"]
for f in caps:  # a cap belongs to the piece whose border it closes
    nb = [g[fpart] for v in f.verts for g in v.link_faces if g not in caps]
    if nb:
        f[fpart] = max(set(nb), key=nb.count)
bm.verts.index_update()
part_of_vert = {}
lab_of_vert = {}
for f in bm.faces:
    for v in f.verts:
        part_of_vert[v.index] = f[fpart]
        lab_of_vert[v.index] = v[vlab]
bm.to_mesh(mesh.data)
bm.free()

# ---- rig ----
arm_data = bpy.data.armatures.new("LegoRig")
rig = bpy.data.objects.new("LegoRig", arm_data)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones
hip = Vector((cx, -0.03 * H, hip_cut + 0.01 * H))
root = eb.new("Root"); root.head = Vector((cx, 0, z0)); root.tail = root.head + Vector((0, 0, 0.1 * H))
body = eb.new("Body"); body.head = hip.copy(); body.tail = hip + Vector((0, 0, 0.3 * H)); body.parent = root
for side in ("L", "R"):
    a, b = arm_axis(side)
    bo = eb.new("Arm" + side); bo.head = a; bo.tail = a + Vector((0, 0, 0.1 * H)); bo.parent = body
    s = 1 if side == "R" else -1
    lg = eb.new("Leg" + side)
    lg.head = Vector((cx + s * 0.075 * H, hip.y, hip_cut + 0.01 * H))
    lg.tail = lg.head + Vector((0, 0, 0.1 * H)); lg.parent = body
hair = eb.new("HairSway")
hair.head = Vector((cx, 0.05 * H, z0 + 0.80 * H)); hair.tail = hair.head + Vector((0, 0, 0.1 * H)); hair.parent = body
bpy.ops.object.mode_set(mode="OBJECT")

groups = {p: mesh.vertex_groups.new(name=p) for p in PIECES}
sway = mesh.vertex_groups.new(name="HairSway")
neck_z = z0 + L["torso_top_z"]
for v in mesh.data.vertices:
    p = PIECES[part_of_vert.get(v.index, 0)]
    t = 0.0
    if p == "Body" and lab_of_vert.get(v.index) in HAIR and v.co.z < neck_z + 0.05 * H:
        t = min(1.0, (neck_z + 0.05 * H - v.co.z) / (0.35 * H)) ** 1.5 * 0.9
    groups[p].add([v.index], 1.0 - t, "REPLACE")
    if t > 0:
        sway.add([v.index], t, "REPLACE")
mesh.parent = rig
mod = mesh.modifiers.new("Armature", "ARMATURE")
mod.object = rig

# ---- animation ----
rig.animation_data_create()
pb = rig.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"


def key(action, frames, fn):
    rig.animation_data.action = action
    for f in frames:
        for b in pb:
            b.rotation_euler = (0, 0, 0)
            b.location = (0, 0, 0)
        fn(f)
        for b in pb:
            b.keyframe_insert("rotation_euler", frame=f)
            b.keyframe_insert("location", frame=f)


def deg(x):
    return math.radians(x)


N = 24
walk = bpy.data.actions.new("Walk")


def walk_pose(f):
    ph = 2 * math.pi * f / N
    s = math.sin(ph)
    pb["LegL"].rotation_euler.x = deg(28) * s
    pb["LegR"].rotation_euler.x = -deg(28) * s
    pb["ArmL"].rotation_euler.x = -deg(22) * s
    pb["ArmR"].rotation_euler.x = deg(22) * s
    pb["Body"].location.y = 0.012 * H * abs(math.cos(ph))  # small bob (bone Y is world up here)
    pb["Body"].rotation_euler.y = deg(3) * s
    pb["HairSway"].rotation_euler.x = deg(6) * math.sin(2 * ph)
    pb["HairSway"].rotation_euler.z = deg(4) * math.sin(ph + 0.6)


key(walk, range(0, N + 1), walk_pose)

idle = bpy.data.actions.new("Idle")


def idle_pose(f):
    ph = 2 * math.pi * f / 48
    pb["Body"].location.y = 0.004 * H * math.sin(ph)
    pb["ArmL"].rotation_euler.x = deg(3) * math.sin(ph)
    pb["ArmR"].rotation_euler.x = deg(3) * math.sin(ph + 1)
    pb["HairSway"].rotation_euler.z = deg(2) * math.sin(ph)


key(idle, range(0, 49, 2), idle_pose)

wave = bpy.data.actions.new("Wave")


def wave_pose(f):
    up = min(1.0, f / 8) if f < 40 else max(0.0, (48 - f) / 8)
    pb["ArmR"].rotation_euler.x = -deg(95) * up
    pb["ArmR"].rotation_euler.y = deg(55) * up
    pb["ArmR"].rotation_euler.z = (deg(14) * math.sin(2 * math.pi * f / 10)) * up
    pb["HairSway"].rotation_euler.z = deg(2) * math.sin(2 * math.pi * f / 24)


key(wave, range(0, 49, 2), wave_pose)

# ---- export ----
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(filepath=dst, use_selection=True, export_animations=True,
                          export_animation_mode="ACTIONS")

# ---- check renders: piece colours (front) + walk/wave frames ----
sc = bpy.context.scene
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        sc.render.engine = e
        break
    except TypeError:
        pass
sc.render.resolution_x, sc.render.resolution_y = 360, 460
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.14, 0.16, 1)
sc.world = w
bpy.ops.object.light_add(type="SUN", rotation=(0.8, 0.2, 0.4)); bpy.context.object.data.energy = 3
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 1.3 * H
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam)
ctr = Vector((cx, 0, z0 + 0.5 * H))
cam.location = ctr + Vector((1.4, -2.6, 0.3)) * H
cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
for act, frames in (("Walk", range(0, N, 1)), ("Wave", range(0, 48, 2))):
    rig.animation_data.action = bpy.data.actions[act]
    for k, f in enumerate(frames):
        sc.frame_set(f)
        sc.render.filepath = str(check / f"{act}-{k:03d}.png")
        bpy.ops.render.render(write_still=True)
# piece colour preview
rig.animation_data.action = None
for b in pb:
    b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0)
cols = [(0.8, 0.8, 0.8, 1), (0.9, 0.2, 0.2, 1), (0.2, 0.4, 0.9, 1), (0.9, 0.7, 0.1, 1), (0.2, 0.8, 0.3, 1)]
mats = []
for i, c in enumerate(cols):
    m = bpy.data.materials.new(f"p{i}"); m.use_nodes = True
    next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs[0].default_value = c
    mats.append(m)
mesh.data.materials.clear()
for m in mats:
    mesh.data.materials.append(m)
for poly in mesh.data.polygons:
    poly.material_index = part_of_vert.get(poly.vertices[0], 0)
cam.location = ctr + Vector((0, -3, 0)) * H
cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = str(check / "pieces.png")
bpy.ops.render.render(write_still=True)
print("DONE")
