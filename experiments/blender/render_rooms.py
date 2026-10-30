"""Cycles stills of the polished dock with the cast in place, as the simulator shows it.

Seats every character who is not on the floor in its room (the simulator's sitCharacter:
hip on rooms.json's seat_z, legs bent 90 degrees, facing the yard) and stands the floor set of
the case at its workstation (stations.py), facing the receiving zone. The cardboard
standees are hidden while the real figures are in. Renders one shot per room from the yard
plus the wide shots.

    Blender -b experiments/blender/out/polish/depo-ok.blend -P experiments/blender/render_rooms.py \
        -- <out dir> [samples] [shot ...]

Shots: room ids (voice, sef, ...), "rooms" for all ten, "genel", "salon"; default: all.
Rendering only room shots seats the whole cast; with a wide shot the ok case's floor
set stands at its stations.
"""

import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATION_B  # noqa: E402

HEIGHT = {"kapi": 2.62, "sef": 2.62}  # PEOPLE[].h in site/sim/index.html; others 2.4
FLOOR_OK = ("spark", "sam", "kapi", "rover")  # FLOOR_BY_CASE.ok in site/sim/index.html
ROOMS = ("voice", "sef", "spark", "sam", "kapi", "ada", "iris", "glimmer", "wonder", "rover")


def import_figure(cid):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(REPO / "site" / "sim" / "models" / f"{cid}.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    # The blob-shadow sphere some exports carry is not part of the figure.
    for o in [o for o in new if o.type == "MESH" and o.parent is None]:
        new.remove(o)
        bpy.data.objects.remove(o)
    arm = next(o for o in new if o.type == "ARMATURE")
    mesh = next(o for o in new if o.type == "MESH")
    s = HEIGHT.get(cid, 2.4) / mesh.dimensions.z
    arm.scale = (s, s, s)
    # The figures face -y as imported; yaw pi turns them toward +y (the yard).
    arm.rotation_mode = "XYZ"
    arm.rotation_euler = (0, 0, math.pi)
    for o in new:
        o.name = f"cast_{cid}_{o.name}"
    return arm, mesh, s


def animate(arm, frames=480):
    """Idle on a loop from a random phase, a Wave now and then (the seated in the simulator)."""
    rnd = random.Random(arm.name)
    ad = arm.animation_data
    clips = {t.name: t.strips[0].action for t in ad.nla_tracks if t.strips}
    ad.action = None
    for t in list(ad.nla_tracks):
        ad.nla_tracks.remove(t)
    idle = ad.nla_tracks.new()
    idle.name = "idle"
    loop = idle.strips.new("idle", -rnd.randint(0, 47), clips["Idle"])
    loop.repeat = frames / 48 + 2
    loop.extrapolation = "HOLD"
    wave = ad.nla_tracks.new(prev=idle)
    wave.name = "wave"
    t0 = rnd.randint(40, 120)
    while t0 < frames - 20:
        w = wave.strips.new(f"wave{t0}", t0, clips["Wave"])
        w.blend_in = w.blend_out = 8
        w.extrapolation = "NOTHING"
        t0 += rnd.randint(160, 300)


def place_cast(floor):
    rooms = json.loads((REPO / "experiments" / "blender" / "out" / "rooms.json").read_text())
    for cid in ROOMS:
        arm, mesh, s = import_figure(cid)
        hip = arm.data.bones["LegL"].head_local.z
        if cid in floor:
            bx, by = STATION_B[cid]
            foot = arm.data.bones["Root"].head_local.z
            arm.location = (bx, by, -foot * s)
            animate(arm)
            continue
        r = rooms[cid]
        arm.location = (r["seat"][0], r["seat"][1], r["seat_z"] - hip * s)
        # Euler legs: the clips key quaternions, so the 90 degree bend survives them.
        for b in ("LegL", "LegR"):
            pb = arm.pose.bones[b]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = (math.pi / 2, 0, 0)
        animate(arm)
    # Like the simulator: only the floor set's stations show; the standees give way.
    idle = tuple(f"p_station_{cid}_" for cid in STATION_B if cid not in floor)
    for o in bpy.data.objects:
        if o.name.startswith(("p_stand_", "p_standft_") + idle):
            o.hide_render = True


def camera(loc, target, lens):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    return cam


def shots():
    out = {}
    for k, cid in enumerate(ROOMS):
        z0 = 0.0 if k < 5 else 3.2
        xc = -15 + 6 * (k % 5) + 3.0
        out[cid] = ((xc + 0.6, -9.6, z0 + 2.0), (xc, -15.8, z0 + 1.3), 22)
    out["genel"] = ((10.8, -9.8, 4.8), (0, 5.3, 0.45), 21)
    out["salon"] = ((0.0, 4.0, 3.2), (0.0, -15.0, 2.6), 18)
    return out


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(args[0] if args else "experiments/blender/out/cycles").resolve()
    samples = int(args[1]) if len(args) > 1 else 96
    want = args[2:] or list(ROOMS) + ["genel", "salon"]
    if "rooms" in want:
        want = [w for w in want if w != "rooms"] + list(ROOMS)
    out.mkdir(parents=True, exist_ok=True)
    # Room portraits seat everyone; the wide shots show the ok case's floor set.
    place_cast(FLOOR_OK if {"genel", "salon"} & set(want) else ())
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.device = "GPU"
    except TypeError:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    all_shots = shots()
    for name in want:
        loc, tgt, lens = all_shots[name]
        sc.camera = camera(loc, tgt, lens)
        sc.render.filepath = str(out / f"{name}.png")
        bpy.ops.render.render(write_still=True)


main()
