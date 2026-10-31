"""Give the simulator's Ada the laptop of her new design (assets/mascots/hero/ada.png).

blender -b -P ada_laptop.py -- <in.glb> <out.glb> [check.png]

The figure (lego_pieces.py output) already wears the mint sweater with the blue infinity
mark; the new design adds a dark grey laptop held open in the hand that does not wave
(Wave lifts ArmR, so it goes on ArmL), its lid's back with the same blue mark. The laptop is
parented to the ArmL bone so it follows Idle, Walk and Wave; rig, actions and names are kept.
"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = args[0], args[1]
check = args[2] if len(args) > 2 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = max((o for o in bpy.data.objects if o.type == "MESH" and o.parent == rig),
           key=lambda o: len(o.data.vertices))
H = body.dimensions.z


def mat(name, hexcol, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    c = tuple(int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
    b.inputs["Base Color"].default_value = (*[x ** 2.2 for x in c], 1)
    b.inputs["Roughness"].default_value = rough
    return m


grey = mat("ada_laptop_grey", "#5a5d63", 0.35)
dark = mat("ada_laptop_keys", "#2b2d31", 0.5)
blue = mat("ada_laptop_mark", "#1877f2", 0.3)

# The ArmL hand: the lowest tenth of the vertices bound to ArmL, in world space.
vg = body.vertex_groups["ArmL"].index
pts = [body.matrix_world @ v.co for v in body.data.vertices
       if any(g.group == vg and g.weight > 0.5 for g in v.groups)]
zmin = min(p.z for p in pts)
zmax = max(p.z for p in pts)
hand = [p for p in pts if p.z < zmin + 0.1 * (zmax - zmin)]
hc = sum(hand, Vector()) / len(hand)
# The figure faces -y; the laptop sits in front of the hand, held open toward Ada.
W, D, T = 0.30 * H, 0.20 * H, 0.014 * H
base_c = Vector((hc.x * 0.55, hc.y - 0.75 * D, hc.z + 0.04 * H))  # in front of the torso
parts = []


def cube(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, size
    o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(o)
    return o


cube("ada_laptop_base", (W, D, T), base_c, grey)
cube("ada_laptop_keys", (W * 0.86, D * 0.62, T * 0.2),
     base_c + Vector((0, 0.05 * D, T * 0.55)), dark)
# Lid hinged at the far edge (away from Ada), tilted back 100 degrees: its back faces -y.
tilt = math.radians(-10)
hinge = base_c + Vector((0, -D / 2, T / 2))
lid_c = hinge + Vector((0, -math.sin(-tilt) * D / 2, math.cos(tilt) * D / 2))
cube("ada_laptop_lid", (W, T, D), lid_c, grey, rot=(tilt, 0, 0))
# Infinity mark on the lid's back: two thin rings side by side.
for k, sx in enumerate((-1, 1)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.026 * H, minor_radius=0.006 * H,
        location=lid_c + Vector((sx * 0.024 * H, -T * 0.6, 0)),
        rotation=(math.radians(90) + tilt, 0, 0))
    o = bpy.context.object
    o.name = f"ada_laptop_mark{k}"
    o.data.materials.append(blue)
    parts.append(o)

bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
laptop = bpy.context.object
laptop.name = "AdaLaptop"
# Follow the ArmL bone, keeping the world transform.
mw = laptop.matrix_world.copy()
laptop.parent = rig
laptop.parent_type = "BONE"
laptop.parent_bone = "ArmL"
laptop.matrix_world = mw

bpy.ops.object.select_all(action="DESELECT")
for o in (rig, body, laptop):
    o.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(filepath=dst, use_selection=True, export_animations=True,
                          export_animation_mode="ACTIONS",
                          export_draco_mesh_compression_enable=True,
                          export_image_format="WEBP")
print("ada_laptop: wrote", dst, "actions", [a.name for a in bpy.data.actions])

if check:
    sc = bpy.context.scene
    for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = e
            break
        except TypeError:
            pass
    sc.render.resolution_x = sc.render.resolution_y = 600
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.5
    sc.world = w
    bpy.ops.object.camera_add(location=(1.2, -3.6, 0.3 * H))
    cam = bpy.context.object
    cam.data.lens = 50
    cam.rotation_euler = (Vector((0, 0, 0.05 * H)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = check
    bpy.ops.render.render(write_still=True)
