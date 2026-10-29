"""Render the Lego cast (or one character) as 1920x1080 PNG frames: walk, then wave.

blender -b -P lego_cast_video.py -- <out_dir> <name> [<name> ...]
Reads assets/mascots/3d/lego/<name>-lego.glb (read only). Encode with ffmpeg afterwards.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
LEGO = ROOT / "assets/mascots/3d/lego"
args = sys.argv[sys.argv.index("--") + 1:]
out, names = Path(args[0]), args[1:]
out.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
cast = []
for i, n in enumerate(names):
    before_obj, before_act = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(LEGO / f"{n}-lego.glb"))
    objs = [o for o in bpy.data.objects if o not in before_obj]
    rig = next(o for o in objs if o.type == "ARMATURE")
    mesh = next(o for o in objs if o.type == "MESH")
    holder = bpy.data.objects.new(f"{n}_holder", None)
    sc.collection.objects.link(holder)
    for o in objs:
        if o.parent is None:
            o.parent = holder
    acts = {a.name.split(".")[0].split("_")[0]: a for a in bpy.data.actions if a not in before_act}
    cast.append((n, rig, mesh, acts))

def bounds(objs_meshes):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for m in objs_meshes:
        ev = m.evaluated_get(dg)
        pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    return [min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]


# normalise heights and line them up (bounds of the posed, deformed mesh)
H = 1.0
gap = 0.8 * H
x0 = -gap * (len(cast) - 1) / 2
for i, (n, rig, mesh, acts) in enumerate(cast):
    holder = bpy.data.objects[f"{n}_holder"]
    bpy.context.view_layer.update()
    lo, hi = bounds([mesh])
    s = H / (hi[2] - lo[2])
    holder.scale = (s, s, s)
    bpy.context.view_layer.update()
    lo, hi = bounds([mesh])
    holder.location = (x0 + i * gap - (lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2])

# the cast shot doesn't need 300k faces per figure; fewer verts = much faster posing per frame
DEC = float(__import__("os").environ.get("LEGO_DECIMATE", "0.25"))
if DEC < 1.0:
    for _, _, m, _ in cast:
        arm_mods = [md for md in m.modifiers if md.type == "ARMATURE"]
        dec = m.modifiers.new("dec", "DECIMATE")
        dec.ratio = DEC
        bpy.context.view_layer.objects.active = m
        while m.modifiers[0] != dec:
            bpy.ops.object.modifier_move_up(modifier="dec")
        bpy.ops.object.modifier_apply(modifier="dec")

# 8K maps are wasted at 1080p for a full-cast shot and slow every frame down
TEX = int(__import__("os").environ.get("LEGO_TEX", "1024"))
for img in bpy.data.images:
    if img.size[0] > TEX:
        img.scale(TEX, TEX)

# look
ENGINE = __import__("os").environ.get("LEGO_ENGINE", "EEVEE")
if ENGINE == "CYCLES":
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for t in ("METAL", "OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = t
            break
        except TypeError:
            pass
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = "GPU"
    sc.cycles.samples = 32
    sc.cycles.use_denoising = True
else:
    for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = e
            break
        except TypeError:
            pass
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 24
try:
    sc.eevee.taa_render_samples = 24
except AttributeError:
    pass
w = bpy.data.worlds.new("w"); w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.86, 0.87, 0.9, 1)
bg.inputs[1].default_value = 0.55
for vt in ("Standard",):
    try:
        sc.view_settings.view_transform = vt  # keep the toy colours saturated
    except TypeError:
        pass
# seamless backdrop: the floor shows the world colour where it recedes, so no horizon line
sc.render.film_transparent = False
sc.world = w
bpy.ops.mesh.primitive_plane_add(size=400)
floor = bpy.context.object
fm = bpy.data.materials.new("floor"); fm.use_nodes = True
next(nd for nd in fm.node_tree.nodes if nd.type == "BSDF_PRINCIPLED").inputs[0].default_value = (0.86, 0.87, 0.9, 1)
floor.data.materials.append(fm)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(25), 0, math.radians(20)))
bpy.context.object.data.energy = 1.6
bpy.ops.object.light_add(type="AREA", location=(0, -4, 3))
bpy.context.object.data.energy = 120
bpy.context.object.data.size = 6
bpy.context.object.rotation_euler = (math.radians(55), 0, 0)

bpy.context.view_layer.update()
lo, hi = bounds([m for _, _, m, _ in cast])
target = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2] + 0.62 * (hi[2] - lo[2])))
width, height = hi[0] - lo[0], hi[2] - lo[2]
cd = bpy.data.cameras.new("cam"); cd.lens = 50; cd.sensor_fit = "HORIZONTAL"
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam)
half = math.atan(cd.sensor_width / (2 * cd.lens))  # horizontal half field of view
dist = max(1.06 * width / 2 / math.tan(half), 1.35 * height / 2 / math.tan(half * 9 / 16))
cam.location = target + Vector((0, -dist, 0.4 * dist))  # looks down enough that the horizon leaves the frame
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam

# timeline: walk cycles (24 f each), then waves (48 f each); fewer for a single figure
segments = [("Walk", 24, 4), ("Wave", 48, 2)] if len(cast) > 1 else [("Walk", 24, 2), ("Wave", 48, 1)]
frame = 0
LIMIT = int(__import__("os").environ.get("LEGO_FRAMES", "100000"))
for act_name, length, reps in segments:
    for r in range(reps):
        for f in range(length):
            for n, rig, mesh, acts in cast:
                rig.animation_data.action = acts.get(act_name)
            if frame >= LIMIT:
                break
            sc.frame_set(f)
            sc.render.filepath = str(out / f"f{frame:04d}.png")
            bpy.ops.render.render(write_still=True)
            frame += 1
print("DONE", frame)
