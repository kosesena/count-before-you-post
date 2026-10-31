"""Render Meshy's waving Glimmer (experiments/glimmer-farewell/wave.glb), front view, transparent.

Usage: Blender -b -P experiments/glimmer_farewell_render.py -- <out_dir> [size] [step]
Writes <out_dir>/f####.png (RGBA). Run with Blender in the background; it never touches an open Blender.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = Path(argv[0]); size = int(argv[1]) if len(argv) > 1 else 720; step = int(argv[2]) if len(argv) > 2 else 1
glb = Path(__file__).resolve().parent / "glimmer-farewell" / "wave.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
sc = bpy.context.scene
meshes = [o for o in sc.objects if o.type == "MESH" and o.name != "Icosphere"]
# Meshy's rig export carries a stray 2 m "Icosphere" helper with no material; it is not part of Glimmer.
for o in sc.objects:
    if o.name == "Icosphere":
        o.hide_render = True
# The figure's box over the whole clip, so the camera frames every pose of the wave.
act = next((o.animation_data.action for o in sc.objects if o.animation_data and o.animation_data.action), None)
f0, f1 = (int(act.frame_range[0]), int(act.frame_range[1])) if act else (1, 1)
lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
for f in range(f0, f1 + 1, 5):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    for o in meshes:
        e = o.evaluated_get(dg)
        for c in e.bound_box:
            w = e.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
centre = (lo + hi) / 2
h = max(hi.z - lo.z, hi.x - lo.x)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
cam.data.lens = 70
dist = h * 2.6
# Meshy rigs face +Z in glTF, which is -Y in Blender: the camera sits on -Y looking at the face.
cam.location = centre + Vector((0, -dist, h * .08))
cam.rotation_euler = (math.radians(90) - math.atan2(h * .08, dist), 0, 0)
sc.camera = cam
for name, loc, energy in (("key", (-1.2, -2, 1.6), 60), ("fill", (1.5, -1.5, .6), 25), ("rim", (0, 2, 2), 40)):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
    L.data.energy = energy; L.data.size = h
    L.location = centre + Vector(loc) * h
    L.rotation_euler = (centre - L.location).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(L)
try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    sc.render.engine = "BLENDER_EEVEE"
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = size
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
out.mkdir(parents=True, exist_ok=True)
for f in range(f0, f1 + 1, step):
    sc.frame_set(f)
    sc.render.filepath = str(out / f"f{f:04d}.png")
    bpy.ops.render.render(write_still=True)
print("frames", f0, f1)
