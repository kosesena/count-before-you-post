"""Put the rigged Lego cast on the dressed-up dock (saved polish scene).

Blender opens the saved scene; this script removes the flat cardboard standees
(p_stand_*, p_standft_*), imports assets/mascots/3d/lego/<name>-lego.glb, stands
each figure on the floor (about 1.6 m tall, Kapi and Sef a little taller)
facing the overview camera like the standee did, and poses them with their
Idle/Wave actions. Round-2 spots: Kapi by the gate barrier/light, Sef at the
receiving-zone edge, Rover east of the forklift, Glimmer on open floor
south-west -- all fully visible in genel. Iris and Ada keep their aisle spots.
Each figure gets a free-standing chest-high name plate (name + English job,
accent stripe in the character colour) facing the same camera. Then:

  blender -b <blend> -P experiments/blender/dock_cast.py -- <out_dir> [stills|move|all]

stills renders genel, teslimat and disari at 1920x1080 to
<out_dir>/cast-<camera>.png; move flies a new FlyCam from outside the truck in
through the dock door over the characters to the pallet (10 s, 24 fps,
1920x1080, H.264) at <out_dir>/cast-move.mp4; all does both. Uses the render
engine the scene already has. The pallet, cartons, labels, jack, gate, barrier,
light, screen, clipboard and DockCam are never touched, and no figure stands
where DockCam can see it. Spark keeps his standee if spark-lego.glb is missing
(and still gets his sign).
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
# Round-2: rover/glimmer moved out of the forklift shadow; iris/ada keep the
# wide aisle between rack rows B and C. All far from DockCam's floor zone.
NEW_SPOTS = {"rover": (9.0, 2.5), "glimmer": (1.0, 0.5),
             "iris": (-6.6, -0.6), "ada": (-9.6, -0.9)}
# Round-2: Kapi next to the gate barrier/light (3.2, 2.4), Sef at the south
# edge of the receiving zone. These override the old standee spots.
GATE_SPOTS = {"kapi": (4.0, 2.0), "sef": (-0.3, 3.0)}
NAMES = {"spark": "Spark", "sam": "Sam", "voice": "Voice", "kapi": "Kap\u0131",
         "sef": "\u015eef", "wonder": "Wonder", "rover": "Rover",
         "glimmer": "Glimmer", "iris": "Iris", "ada": "Ada"}
ROLES = {"spark": "reads the note", "sam": "counts the cartons",
         "voice": "hears the receiver", "kapi": "the gate",
         "sef": "signs off", "wonder": "checks and writes the paperwork",
         "rover": "reads the note again",
         "glimmer": "the other open-weight reader",
         "iris": "drew the cast", "ada": "wrote the code"}
ACCENT = {"spark": "#f97316", "sam": "#3b82f6", "voice": "#1e3a8a",
          "kapi": "#a16207", "sef": "#1d4ed8", "wonder": "#ca8a04",
          "rover": "#0d9488", "glimmer": "#8b5cf6", "iris": "#db2777",
          "ada": "#0f766e"}
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
# Keep-outs the figures (and their signs) must avoid: DockCam floor zone,
# pallet, gate/barrier, screen, clipboard (x, y, clearance radius).
DOCKCAM_ZONE = (-2.5, 3.5, 2.5, 7.5)
AVOID_PTS = [(0.0, 5.5, 1.1), (3.2, 2.4, 0.7), (3.6, 2.4, 0.6),
             (-3.6, 2.6, 1.1), (-3.0, 5.6, 0.7)]
AVOID_BARRIER = (0.4, 3.6, 2.28, 2.52)
# Big occluders the signs must stay clear of (from warehouse.py p_racks,
# p_office, p_forklift): (row y, bay xs), office and forklift x0,y0,x1,y1.
RACK_ROWS = [(8.5, (-11.9, -9.2, -6.5)), (6.0, (-11.9, -9.2)),
             (-2.5, (-12.5, -9.8, -7.1)), (-5.0, (-12.5, -9.8)),
             (-7.5, (-12.5, -9.8, -7.1))]
OFFICE_BOX = (9.2, 4.4, 12.8, 8.1)
FORKLIFT_BOX = (7.4, -1.7, 8.6, 1.85)


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
    if name in GATE_SPOTS:
        x, y = GATE_SPOTS[name]
        yaw = math.atan2(cam_xy[0] - x, -(cam_xy[1] - y))
    elif name in spots:
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


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def sign_mat(name, color, rough=0.6):
    """Reuse the dock's sign material when the saved scene has it."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    try:
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Roughness"].default_value = rough
    except (StopIteration, KeyError, AttributeError, TypeError):
        pass
    return m


def sign_box(name, dims, loc, m, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc,
                                    rotation=(0, 0, rot_z))
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    try:
        ob.data.materials.append(m)
    except (AttributeError, TypeError):
        pass
    return ob


def sign_cyl(name, r, h, loc, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc,
                                        vertices=16)
    ob = bpy.context.object
    ob.name = name
    try:
        ob.data.materials.append(m)
    except (AttributeError, TypeError):
        pass
    return ob


_font_tried = []


def sign_font():
    if _font_tried:
        return _font_tried[0]
    _font_tried.append(None)
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"):
        try:
            if Path(p).exists():
                _font_tried[0] = bpy.data.fonts.load(p, check_existing=True)
                break
        except (RuntimeError, TypeError, OSError):
            continue
    return _font_tried[0]


def sign_text(name, body, loc, size, m, yaw):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    f = sign_font()
    if f is not None:
        try:
            curve.font = f
        except (AttributeError, TypeError):
            pass
    curve.size, curve.extrude = size, 0.002
    try:
        curve.align_x, curve.align_y = "CENTER", "CENTER"
    except (AttributeError, TypeError):
        pass
    ob = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, yaw)
    try:
        ob.data.materials.append(m)
    except (AttributeError, TypeError):
        pass
    return ob


def sign_blocked(sx, sy):
    x0, y0, x1, y1 = DOCKCAM_ZONE
    if x0 - 0.1 <= sx <= x1 + 0.1 and y0 - 0.1 <= sy <= y1 + 0.1:
        return True
    bx0, bx1, by0, by1 = AVOID_BARRIER
    if bx0 - 0.3 <= sx <= bx1 + 0.3 and by0 - 0.3 <= sy <= by1 + 0.3:
        return True
    for px, py, r in AVOID_PTS:
        if math.hypot(sx - px, sy - py) < r:
            return True
    for ry, bays in RACK_ROWS:
        if ry - 1.1 <= sy <= ry + 1.1:
            for bx in bays:
                if bx - 1.89 <= sx <= bx + 1.89:
                    return True
    ox0, oy0, ox1, oy1 = OFFICE_BOX
    if ox0 - 0.4 <= sx <= ox1 + 0.4 and oy0 - 0.4 <= sy <= oy1 + 0.4:
        return True
    fx0, fy0, fx1, fy1 = FORKLIFT_BOX
    if fx0 - 0.4 <= sx <= fx1 + 0.4 and fy0 - 0.4 <= sy <= fy1 + 0.4:
        return True
    return False


def in_teslimat(x, y):
    if y < 0.3:
        return False
    ang = math.degrees(math.atan2(y - CAM_SPOTS["teslimat"][1],
                                  x - CAM_SPOTS["teslimat"][0]))
    return 92.0 <= ang <= 166.0


def make_sign(name, fx, fy, yaw, cam_xy, others):
    """Chest-high name plate on a slim post beside the figure, facing genel."""
    job = ROLES[name]
    plate_w = min(1.25, max(0.85, len(job) * 0.04 + 0.30))
    plate_h, plate_z, thick = 0.42, 1.18, 0.03
    off = plate_w / 2 + 0.35
    dx, dy = cam_xy[0] - fx, cam_xy[1] - fy
    dl = math.hypot(dx, dy) or 1.0
    cx, cy = dx / dl, dy / dl
    px, py = -cy, cx
    cands = [(fx + px * off, fy + py * off),
             (fx - px * off, fy - py * off)]
    scored = []
    fig_in = in_teslimat(fx, fy)
    for sx, sy in cands:
        blocked = sign_blocked(sx, sy)
        md = min((math.hypot(sx - ox, sy - oy) for ox, oy in others),
                 default=99.0)
        out_frame = 1 if (fig_in and not in_teslimat(sx, sy)) else 0
        scored.append((blocked, out_frame, -md, (sx, sy)))
    scored.sort()
    sx, sy = scored[0][3]
    paper = sign_mat("paper", (0.95, 0.95, 0.93))
    ink = sign_mat("ink", (0.02, 0.02, 0.02))
    dark = bpy.data.materials.get("dark") or \
        bpy.data.materials.get("p_dark_steel")
    if dark is None:
        dark = sign_mat("cast_post", (0.06, 0.06, 0.07), rough=0.5)
    accent = sign_mat(f"cast_accent_{name}", hex_rgb(ACCENT[name]), rough=0.5)
    post_h = plate_z - plate_h / 2
    sign_cyl(f"cast_signpost_{name}", 0.022, post_h,
             (sx, sy, post_h / 2), dark)
    sign_box(f"cast_sign_{name}", (plate_w, thick, plate_h),
             (sx, sy, plate_z), paper, rot_z=yaw)
    sign_box(f"cast_signstripe_{name}", (plate_w + 0.004, thick + 0.004, 0.055),
             (sx, sy, plate_z + plate_h / 2 - 0.0275), accent, rot_z=yaw)
    gap = thick / 2 + 0.006
    tx, ty = sx + cx * gap, sy + cy * gap
    sign_text(f"cast_signname_{name}", NAMES[name],
              (tx, ty, plate_z + 0.085), 0.135, ink, yaw)
    js = min(0.078, (plate_w - 0.10) / (max(len(job), 1) * 0.58))
    sign_text(f"cast_signjob_{name}", job,
              (tx, ty, plate_z - 0.105), max(js, 0.042), ink, yaw)
    log(f"sign {name}: pos=({sx:.2f}, {sy:.2f}) w={plate_w:.2f} "
        f"job_size={max(js, 0.042):.3f}")
    return sx, sy


def setup_signs(figinfo, cam_xy):
    pts = [(v["x"], v["y"]) for v in figinfo.values()]
    for name in ORDER:
        if name not in figinfo:
            continue
        v = figinfo[name]
        others = [(x, y) for x, y in pts
                  if math.hypot(x - v["x"], y - v["y"]) > 1e-6]
        make_sign(name, v["x"], v["y"], v["yaw"], cam_xy, others)


def own_names(anchor):
    out, stack = set(), [anchor]
    while stack:
        ob = stack.pop()
        out.add(ob.name)
        stack.extend(list(ob.children))
    return out


def check_genel_visibility(cams, figinfo):
    """Ray-cast from the genel camera to each figure's body samples."""
    genel = cams["genel"]
    cam_loc = Vector(genel.location)
    bpy.context.view_layer.update()
    try:
        depsgraph = bpy.context.evaluated_depsgraph_get()
    except (AttributeError, RuntimeError) as e:
        log(f"visibility check skipped ({e})")
        return
    scene = bpy.context.scene
    for name in ORDER:
        if name not in figinfo:
            continue
        v = figinfo[name]
        x, y, h, own = v["x"], v["y"], v["h"], v["own"]
        samples = [(x, y, 0.20), (x, y, 0.80), (x, y, 1.20),
                   (x, y, max(h - 0.08, 1.30))]
        clear, blocks = 0, []
        for s in samples:
            tgt = Vector(s)
            vec = tgt - cam_loc
            dist = vec.length
            if dist < 1e-6:
                continue
            try:
                res = scene.ray_cast(depsgraph, cam_loc, vec.normalized())
            except (RuntimeError, TypeError):
                clear += 1
                continue
            hit = bool(res[0]) if len(res) else False
            if not hit:
                clear += 1
                continue
            loc = res[1]
            obj = None
            for item in res[2:]:
                if item is not None and hasattr(item, "name") and \
                        hasattr(item, "type"):
                    obj = item
                    break
            if obj is None or obj.name in own:
                clear += 1
                continue
            try:
                hd = (Vector(loc) - cam_loc).length
            except (TypeError, AttributeError):
                clear += 1
                continue
            if hd >= dist - 0.12:
                clear += 1
            else:
                blocks.append(f"{s[2]:.2f}m by {obj.name}")
        state = "VISIBLE" if clear == len(samples) else "OCCLUDED"
        extra = "" if state == "VISIBLE" else f" ({'; '.join(blocks)})"
        log(f"genel visibility {name} at ({x:.2f}, {y:.2f}): {state} "
            f"{clear}/{len(samples)} samples clear{extra}")


def setup_cast(cams):
    spots = read_standees()
    keep_spark = not (LEGO / "spark-lego.glb").exists()
    if keep_spark:
        log("spark-lego.glb missing, Spark keeps his standee")
    clear_standees(keep_spark)
    cam_xy = (cams["genel"].location.x, cams["genel"].location.y)
    placed, figinfo = [], {}
    for i, name in enumerate(ORDER):
        if name not in spots and name not in NEW_SPOTS \
                and name not in GATE_SPOTS:
            continue
        anchor = place_one(name, spots, cam_xy, i * 7)
        if anchor is not None:
            placed.append(name)
            figinfo[name] = {"x": anchor.location.x, "y": anchor.location.y,
                             "yaw": anchor.rotation_euler.z,
                             "h": TALL_H if name in TALL else HEIGHT,
                             "own": own_names(anchor)}
    if keep_spark and "spark" in spots and "spark" not in figinfo:
        x, y, yaw = spots["spark"]
        own = {o.name for o in bpy.data.objects if "spark" in o.name and
               (o.name.startswith("p_stand_") or
                o.name.startswith("p_standft_"))}
        figinfo["spark"] = {"x": x, "y": y, "yaw": yaw, "h": 2.1, "own": own}
        log(f"spark (standee): pos=({x:.2f}, {y:.2f}, 0.00) h=2.10")
    setup_signs(figinfo, cam_xy)
    check_genel_visibility(cams, figinfo)
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


def lighten(max_verts=150_000, samples=16):
    """For the camera move only: the Lego meshes are 3M+ vertices each, and deforming them
    made a 1080p frame take one to four minutes. The figures pass at a distance, so each mesh
    is decimated on its rest shape (before the armature, applied once) and EEVEE takes fewer
    samples. The stills keep the full meshes."""
    for ob in [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > max_verts]:
        if ob.data.shape_keys:
            continue
        dec = ob.modifiers.new("lighten", "DECIMATE")
        dec.ratio = max_verts / len(ob.data.vertices)
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_move_to_index(modifier=dec.name, index=0)
            bpy.ops.object.modifier_apply(modifier=dec.name)
        log(f"lighten {ob.name}: {len(ob.data.vertices)} vertices")
    eevee = bpy.context.scene.eevee
    if hasattr(eevee, "taa_render_samples"):
        eevee.taa_render_samples = samples


def do_move(out):
    lighten()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
    scene.render.resolution_percentage = 100
    scene.render.fps, scene.frame_start, scene.frame_end = \
        FPS, 1, MOVE_FRAMES
    try:
        scene.render.fps_base = 1.0
    except (TypeError, AttributeError):
        pass
    # This Blender build has no FFmpeg output: frames go out as PNG and are joined with
    # ffmpeg afterwards (`ffmpeg -framerate 24 -i <out>/move/f_%04d.png -c:v libx264
    # -pix_fmt yuv420p -crf 18 <out>/cast-move.mp4`).
    scene.render.image_settings.file_format = "PNG"
    (out / "move").mkdir(parents=True, exist_ok=True)
    log(f"frames as PNG, engine={scene.render.engine}")
    scene.camera = flycam()
    scene.render.filepath = str(out / "move" / "f_")
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
