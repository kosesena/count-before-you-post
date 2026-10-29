"""Put the rigged Lego cast on the dressed-up dock (saved polish scene).

Blender opens the saved scene; this script removes the flat cardboard standees
(p_stand_*, p_standft_*), imports assets/mascots/3d/lego/<name>-lego.glb, stands
each figure on the floor at its standee's spot (about 1.6 m tall, Kapi and Sef a
little taller) facing the overview camera like the standee did, and poses them
with their Idle/Wave actions. Rover, Glimmer, Iris and Ada had no standee; they
join near the office and the racks where they cover no main subject. Then:

  blender -b <blend> -P experiments/blender/dock_cast.py -- <out_dir> [stills|move|all]

stills renders genel, teslimat and disari at 1920x1080 to
<out_dir>/cast-<camera>.png; move flies a new FlyCam from outside the truck in
through the dock door over the characters to the pallet (10 s, 24 fps,
1920x1080, H.264) at <out_dir>/cast-move.mp4; all does both. Uses the render
engine the scene already has. The pallet, cartons, labels, jack, gate, barrier,
light, screen, clipboard and DockCam are never touched, and no figure stands
where DockCam can see it. Spark keeps his standee if spark-lego.glb is missing.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
LEGO = REPO / "assets" / "mascots" / "3d" / "lego"

HEIGHT, TALL_H = 1.6, 1.75
TALL = {"kapi", "sef"}
WAVE = {"spark", "kapi"}
ORDER = ("sam", "voice", "wonder", "kapi", "sef", "spark",
         "rover", "glimmer", "iris", "ada")
CUTOUTS = {"spark": "spark", "sam": "sam", "voice": "voice",
           "wonder": "wonder", "kapi-gec": "kapi", "kapi-dur": "kapi",
           "sef": "sef"}
# New figures near the office glass front (rover, glimmer) and in the wide
# aisle between rack rows B and C (iris, ada): all visible in the genel wide
# shot, out of the tighter teslimat frame, and far from DockCam's floor zone.
NEW_SPOTS = {"rover": (8.5, 6.2), "glimmer": (7.0, 7.1),
             "iris": (-6.6, -0.6), "ada": (-9.6, -0.9)}
# The polish cameras are not named in the file; find them by where they stand.
CAM_SPOTS = {"genel": (10.8, -9.8, 4.8), "teslimat": (4.4, 0.0, 5.4),
             "disari": (8.0, 26.5, 3.4)}
FPS, MOVE_FRAMES = 24, 240
STILL_FRAME = 24
# FlyCam waypoints: along the trailer's east side, through the door opening
# (x in [-1.6, 1.6], camera at z ~2.1 passes under the lintel), over the
# receiving zone, ending near the teslimat camera on the pallet.
FLY_POS = [(7.0, 27.5, 3.6), (5.0, 21.5, 3.0), (2.8, 16.0, 2.5),
           (0.9, 10.6, 2.05), (0.7, 8.6, 2.15), (3.2, 6.0, 2.8),
           (2.2, 2.8, 3.4), (3.88, 0.62, 4.81)]
FLY_LOOK = [(0, 16.5, 1.3), (0, 14.0, 1.6), (0, 11.5, 1.8), (0, 8.5, 1.4),
            (1.5, 6.0, 1.0), (-1.0, 4.5, 0.8), (-0.5, 5.0, 0.6),
            (0, 5.3, 0.4)]


def log(msg):
    print(f"[dock_cast] {msg}", flush=True)


def pick_enum(owner, prop, candidates):
    """First candidate the API offers for an enum property (None if none)."""
    try:
        items = owner.bl_rna.properties[prop].enum_items
        have = {it.identifier for it in items}
    except (KeyError, AttributeError, TypeError):
        return candidates[0]
    for cand in candidates:
        if cand in have:
            return cand
    return None


def aim(cam, target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat(
        "-Z", "Y").to_euler()


def catmull(points, t):
    """Uniform Catmull-Rom through 3D points at t in [0, 1]."""
    n = len(points) - 1
    x = min(max(t, 0.0), 1.0) * n
    i = min(int(x), n - 1)
    f = x - i
    p0, p1, p2, p3 = (points[max(i - 1, 0)], points[i], points[i + 1],
                      points[min(i + 2, n)])
    f2, f3 = f * f, f * f * f
    return [0.5 * ((2 * b) + (-a + c) * f + (2 * a - 5 * b + 4 * c - d) * f2 +
                   (-a + 3 * b - 3 * c + d) * f3)
            for a, b, c, d in zip(p0, p1, p2, p3)]


def find_cameras():
    """Map genel/teslimat/disari to objects by their polish positions."""
    cams = [o for o in bpy.data.objects if o.type == "CAMERA"]
    found, taken = {}, set()
    for name, spot in CAM_SPOTS.items():
        best = min((o for o in cams if o not in taken),
                   key=lambda o: (Vector(o.location) - Vector(spot)).length,
                   default=None)
        if best is None or (Vector(best.location) - Vector(spot)).length > 1.0:
            raise RuntimeError(f"camera {name} not found near {spot}")
        found[name] = best
        taken.add(best)
        log(f"camera {name} -> {best.name} at "
            f"{tuple(round(v, 2) for v in best.location)}")
    return found


def read_standees():
    """Where each standee stood and which way it faced: char -> (x, y, yaw)."""
    spots = {}
    for ob in bpy.data.objects:
        if not ob.name.startswith("p_stand_") or \
                ob.name.startswith("p_standft_"):
            continue
        char = CUTOUTS.get(ob.name[len("p_stand_"):].rsplit(".", 1)[0])
        if char:
            spots[char] = (ob.location.x, ob.location.y, ob.rotation_euler.z)
    return spots


def clear_standees(keep_spark):
    """Delete the cardboard standees and their feet."""
    for ob in list(bpy.data.objects):
        if ob.name.startswith("p_stand_") or ob.name.startswith("p_standft_"):
            if keep_spark and "spark" in ob.name:
                continue
            bpy.data.objects.remove(ob, do_unlink=True)


def import_glb(path):
    before_o, before_a = set(bpy.data.objects), set(bpy.data.actions)
    try:
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
    except (RuntimeError, TypeError):
        pass
    bpy.ops.import_scene.gltf(filepath=str(path))
    return ([o for o in bpy.data.objects if o not in before_o],
            [a for a in bpy.data.actions if a not in before_a])


def zbounds(meshes):
    bpy.context.view_layer.update()
    zs = [(m.matrix_world @ Vector(c)).z
          for m in meshes for c in m.bound_box]
    return min(zs), max(zs)


def fcurves_of(action):
    try:
        if len(action.fcurves):
            return list(action.fcurves)
    except (AttributeError, TypeError):
        pass
    out = []
    try:
        for layer in getattr(action, "layers", []):
            for strip in getattr(layer, "strips", []):
                for bag in getattr(strip, "channelbags", []):
                    out.extend(list(getattr(bag, "fcurves", [])))
    except (AttributeError, TypeError):
        pass
    return out


def loop_action(action, offset):
    """Loop the action forever and shift its phase by offset frames."""
    for fc in fcurves_of(action):
        cyc = pick_enum(fc, "extrapolation", ["CYCLES"])
        if cyc:
            try:
                fc.extrapolation = cyc
            except (TypeError, AttributeError):
                pass
        if offset:
            for kp in fc.keyframe_points:
                kp.co.x += offset
                kp.handle_left.x += offset
                kp.handle_right.x += offset
            try:
                fc.update()
            except (RuntimeError, AttributeError):
                pass


def assign_action(rig, actions, kind, offset):
    base = {a.name.split(".")[0]: a for a in actions}
    action = base.get(kind)
    if action is None:
        log(f"no {kind} action for {rig.name}, left unposed")
        return
    if rig.animation_data is None:
        rig.animation_data_create()
    want = rig.name
    try:
        slot = getattr(rig.animation_data, "action_slot", None)
        want = slot.name if slot else rig.name
    except (AttributeError, TypeError):
        pass
    rig.animation_data.action = action
    try:
        slots = list(getattr(action, "slots", []) or [])
        if slots and hasattr(rig.animation_data, "action_slot"):
            rig.animation_data.action_slot = next(
                (s for s in slots if want in s.name), slots[0])
    except (AttributeError, TypeError, RuntimeError):
        pass
    loop_action(action, offset)


def place_one(name, spots, cam_xy, offset):
    """Import the figure, scale to height, ground it at its spot, pose it."""
    glb = LEGO / f"{name}-lego.glb"
    if not glb.exists():
        return None
    if name in spots:
        x, y, yaw = spots[name]
    else:
        x, y = NEW_SPOTS[name]
        yaw = math.atan2(cam_xy[0] - x, -(cam_xy[1] - y))
    objs, actions = import_glb(glb)
    meshes = [o for o in objs if o.type == "MESH"]
    rigs = [o for o in objs if o.type == "ARMATURE"]
    anchor = bpy.data.objects.new(f"cast_{name}", None)
    bpy.context.scene.collection.objects.link(anchor)
    new = set(objs)
    for ob in objs:
        if ob.parent is None or ob.parent not in new:
            ob.parent = anchor
            try:
                ob.matrix_parent_inverse.identity()
            except (AttributeError, TypeError):
                pass
    height = TALL_H if name in TALL else HEIGHT
    z0, z1 = zbounds(meshes)
    s = height / (z1 - z0)
    anchor.scale = (s, s, s)
    anchor.rotation_euler = (0, 0, yaw)
    anchor.location = (x, y, 0)
    anchor.location.z -= zbounds(meshes)[0]
    if rigs:
        assign_action(rigs[0], actions,
                      "Wave" if name in WAVE else "Idle", offset)
    log(f"{name}: pos=({x:.2f}, {y:.2f}, 0.00) yaw={math.degrees(yaw):.1f} "
        f"scale={s:.4f} h={height:.2f}")
    return anchor


def setup_cast(cams):
    spots = read_standees()
    keep_spark = not (LEGO / "spark-lego.glb").exists()
    if keep_spark:
        log("spark-lego.glb missing, Spark keeps his standee")
    clear_standees(keep_spark)
    cam_xy = (cams["genel"].location.x, cams["genel"].location.y)
    placed = []
    for i, name in enumerate(ORDER):
        if name not in spots and name not in NEW_SPOTS:
            continue
        if place_one(name, spots, cam_xy, i * 7) is not None:
            placed.append(name)
    bpy.context.scene.frame_set(STILL_FRAME)
    return placed


def do_stills(out, cams):
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    fmt = pick_enum(scene.render.image_settings, "file_format", ["PNG"])
    if fmt:
        try:
            scene.render.image_settings.file_format = fmt
        except (TypeError, AttributeError):
            pass
    scene.frame_set(STILL_FRAME)
    for name in ("genel", "teslimat", "disari"):
        scene.camera = cams[name]
        scene.render.filepath = str(out / f"cast-{name}.png")
        bpy.ops.render.render(write_still=True)
        log(f"wrote {scene.render.filepath}")
    scene.camera = cams["genel"]


def flycam():
    old = bpy.data.objects.get("FlyCam")
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    data = bpy.data.cameras.new("FlyCam")
    data.lens = 24
    cam = bpy.data.objects.new("FlyCam", data)
    bpy.context.scene.collection.objects.link(cam)
    for f in range(1, MOVE_FRAMES + 1):
        t = (f - 1) / (MOVE_FRAMES - 1)
        eased = 0.5 - 0.5 * math.cos(math.pi * t)
        cam.location = catmull(FLY_POS, eased)
        aim(cam, catmull(FLY_LOOK, eased))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    return cam


def do_move(out):
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    scene.render.fps, scene.frame_start, scene.frame_end = \
        FPS, 1, MOVE_FRAMES
    try:
        scene.render.fps_base = 1.0
    except (TypeError, AttributeError):
        pass
    fmt = pick_enum(scene.render.image_settings, "file_format", ["FFMPEG"])
    if fmt:
        try:
            scene.render.image_settings.file_format = fmt
        except (TypeError, AttributeError):
            pass
    ff = scene.render.ffmpeg
    container = pick_enum(ff, "format", ["MPEG4"])
    if container:
        try:
            ff.format = container
        except (TypeError, AttributeError):
            pass
    codec = pick_enum(ff, "codec", ["H264"])
    if codec:
        try:
            ff.codec = codec
        except (TypeError, AttributeError):
            pass
    log(f"video container={container} codec={codec} engine={scene.render.engine}")
    scene.camera = flycam()
    scene.render.filepath = str(out / "cast-move.mp4")
    bpy.ops.render.render(animation=True)
    log(f"wrote {scene.render.filepath}")


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    if not args:
        raise SystemExit("usage: dock_cast.py <out_dir> [stills|move|all]")
    out, mode = Path(args[0]).resolve(), (args[1] if len(args) > 1 else "all")
    if mode not in ("stills", "move", "all"):
        raise SystemExit(f"unknown mode {mode!r}, want stills|move|all")
    out.mkdir(parents=True, exist_ok=True)
    cams = find_cameras()
    log(f"cast: {', '.join(setup_cast(cams))}")
    if mode in ("stills", "all"):
        do_stills(out, cams)
    if mode in ("move", "all"):
        do_move(out)


if __name__ == "__main__":
    main()
