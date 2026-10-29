"""Make a Lego GLB light enough for the browser without a visible loss.

Usage: blender -b -P experiments/web/compress_glb.py -- <in.glb> <out.glb> [max_tris] [max_tex]
Defaults: 150k triangles, 2048 px textures. Meshes are decimated on their rest shape (the
armature and the Walk/Idle/Wave actions stay), textures are scaled down only when larger
than max_tex and written as WebP (quality 90), and the meshes are Draco-compressed. Prints
the triangle count and texture sizes before and after, and the file size.
"""
import sys
from pathlib import Path

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
src, dst = Path(args[0]), Path(args[1])
MAX_TRIS = int(args[2]) if len(args) > 2 else 150_000
MAX_TEX = int(args[3]) if len(args) > 3 else 2048


def tris(meshes):
    return sum(sum(len(p.vertices) - 2 for p in m.data.polygons) for m in meshes)


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
before = tris(meshes)
ratio = min(1.0, MAX_TRIS / max(before, 1))
for ob in meshes:
    if ratio >= 1.0 or ob.data.shape_keys:
        continue
    dec = ob.modifiers.new("web", "DECIMATE")
    dec.ratio = ratio
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
        bpy.ops.object.modifier_apply(modifier=dec.name)

sizes = []
for img in bpy.data.images:
    w, h = img.size
    if max(w, h) > MAX_TEX:
        s = MAX_TEX / max(w, h)
        img.scale(round(w * s), round(h * s))
    sizes.append(f"{img.name} {w}x{h}->{img.size[0]}x{img.size[1]}")

bpy.ops.export_scene.gltf(
    filepath=str(dst), export_format="GLB", export_animations=True,
    export_image_format="WEBP", export_image_quality=90,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12)
print(f"WEB {src.name}: {before} -> {tris(meshes)} triangles; "
      f"{src.stat().st_size / 1e6:.1f} MB -> {dst.stat().st_size / 1e6:.2f} MB")
for s in sizes:
    print("WEB tex", s)
print("WEB actions", [a.name for a in bpy.data.actions])
