"""A short walk-around clip of the dock, as a receiver with a camera (or glasses) would film it.

Usage: blender -b -P experiments/blender/dock_clip.py -- <out_dir> <variant> [seconds]
Writes <out_dir>/frames-<variant>/####.png; experiments/dock_clip.sh turns them into an mp4.
The camera walks an arc around the pallet at eye height, so cartons hidden from the ceiling
camera (the stacked load) come into view from the side.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).parent))
from warehouse import aim, build  # noqa: E402

FPS = 12
CENTER = (0.0, 5.5)  # the pallet, as in warehouse.build
RADIUS, EYE, LOOK_Z = 2.6, 1.65, 0.7


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    out, variant = Path(args[0]).resolve(), args[1]
    seconds = float(args[2]) if len(args) > 2 else 6
    build(variant)
    scene = bpy.context.scene
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.lens = 24
    scene.camera = cam

    # From the left side, past the front, to the right side: away from the truck behind.
    frames = int(seconds * FPS)
    start, end = math.radians(195), math.radians(345)
    for f in range(frames):
        t = f / (frames - 1)
        a = start + (end - start) * (0.5 - 0.5 * math.cos(math.pi * t))  # ease in and out
        cam.location = (CENTER[0] + RADIUS * math.cos(a), CENTER[1] + RADIUS * math.sin(a),
                        EYE + 0.03 * math.sin(f * 0.9))  # a little walking bob
        aim(cam, (CENTER[0], CENTER[1], LOOK_Z))
        cam.keyframe_insert("location", frame=f + 1)
        cam.keyframe_insert("rotation_euler", frame=f + 1)

    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, frames
    scene.render.filepath = str(out / f"frames-{variant}" / "####")
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
