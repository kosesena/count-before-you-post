"""Six floor workstations for the polished dock (the `ok` case).

Mirrors the simulator's `// ---------- floor stations ----------` section in
`site/sim/index.html` (`STATION_JOB`, `STATION_IDS`, `padGeo`, `signTexture`,
`buildSparkFurniture` .. `buildRoverFurniture`, `buildStation`, `PEOPLE[].b`).
Blender `(x, y, z)` is the simulator's `(x, y)` floor position plus height `z`;
station-local three.js `(lx, ly, lz)` is Blender `(b[0]+lx, b[1]-lz, ly)`.
Three.js `BoxGeometry(w, h, d)` becomes Blender dims `(w, d, h)`.
"""

import bpy
import math

# Station bases b from PEOPLE in site/sim/index.html (spark, sam, kapi, wonder, sef, rover).
STATION_B = {
    "spark": (-4.7, 0.9),
    "sam": (1.4, 1.2),
    "kapi": (4.4, 2.0),
    "wonder": (-5.9, 0.4),
    "sef": (-1.6, -0.9),
    "rover": (-0.6, -0.6),
}
# Job lines from STATION_JOB in site/sim/index.html.
STATION_JOB = {
    "spark": "reads the note",
    "sam": "counts the cartons",
    "kapi": "the gate decides",
    "wonder": "writes the paperwork",
    "sef": "signs off",
    "rover": "reads it a second time",
}
# Display names from PEOPLE[].name in site/sim/index.html.
STATION_NAME = {
    "spark": "Spark",
    "sam": "Sam",
    "kapi": "Kapı",
    "wonder": "Wonder",
    "sef": "Şef",
    "rover": "Rover",
}
# Character colours from CHAR_COL_FALLBACK in site/sim/index.html.
STATION_COL = {
    "spark": "#f97316",
    "sam": "#3b82f6",
    "kapi": "#a16207",
    "wonder": "#ca8a04",
    "sef": "#1d4ed8",
    "rover": "#0d9488",
}


def build_stations(P, box, cyl, mat, ids=("spark", "sam", "kapi", "wonder", "sef", "rover")):
    """Build floor workstations into collection `stations` (the `ok` case).

    `P` is the polish-materials dict (unused: stations keep simulator colours);
    `box`, `cyl`, `mat` are the helpers from `experiments/blender/warehouse.py`.
    `ids` selects which stations to build (one case's floor set).
    Dynamic-only pieces are skipped: Wonder's stack stays empty, Sef's red
    stamp mark stays hidden, Spark's turning page is one static sheet.
    """
    _ = P

    def _srgb_u(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def _lin(v):
        if isinstance(v, int):
            r = ((v >> 16) & 255) / 255.0
            g = ((v >> 8) & 255) / 255.0
            b = (v & 255) / 255.0
        else:
            h = v.lstrip("#")
            r = int(h[0:2], 16) / 255.0
            g = int(h[2:4], 16) / 255.0
            b = int(h[4:6], 16) / 255.0
        return (_srgb_u(r), _srgb_u(g), _srgb_u(b))

    def _hexkey(v):
        return f"{v:06x}" if isinstance(v, int) else v.lstrip("#").lower()

    def _mat(v, rough=0.75, metal=0.05, emit=0.0):
        return mat(f"p_station_m_{_hexkey(v)}_r{rough:g}_m{metal:g}_e{emit:g}",
                   _lin(v), rough, metal, emit)

    def _emit_mat(name, base, emitc, strength, rough=0.4):
        found = bpy.data.materials.get(name)
        if found:
            return found
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*_lin(base), 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = 0.0
        b.inputs["Emission Color"].default_value = (*_lin(emitc), 1)
        b.inputs["Emission Strength"].default_value = strength
        return m

    col = bpy.data.collections.get("stations")
    if col is None:
        col = bpy.data.collections.new("stations")
        bpy.context.scene.collection.children.link(col)

    def _move(ob):
        for c in list(ob.users_collection):
            try:
                c.objects.unlink(ob)
            except RuntimeError:
                pass
        col.objects.link(ob)

    def _empty(name, loc, rot=(0.0, 0.0, 0.0), parent=None):
        ob = bpy.data.objects.new(name, None)
        col.objects.link(ob)
        if parent is not None:
            ob.parent = parent
            ob.matrix_parent_inverse.identity()
        ob.location = loc
        ob.rotation_euler = rot
        return ob

    def _parent(ob, parent, loc, rot=None, mode=None):
        if mode:
            ob.rotation_mode = mode
        ob.parent = parent
        ob.matrix_parent_inverse.identity()
        ob.location = loc
        if rot is not None:
            ob.rotation_euler = rot
        _move(ob)
        return ob

    def _place(ob, loc, rot=None, mode=None):
        if mode:
            ob.rotation_mode = mode
        ob.location = loc
        if rot is not None:
            ob.rotation_euler = rot
        _move(ob)
        return ob

    def _cone(name, rbot, rtop, h, m, verts=24):
        bpy.ops.mesh.primitive_cone_add(radius1=rbot, radius2=rtop, depth=h,
                                        location=(0, 0, 0), vertices=verts)
        ob = bpy.context.object
        ob.name = name
        ob.data.materials.append(m)
        return ob

    def _sphere(name, r, m):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, 0))
        ob = bpy.context.object
        ob.name = name
        ob.data.materials.append(m)
        return ob

    def _plane(name, w, h, m):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        ob = bpy.context.object
        ob.name = name
        ob.scale = (w, h, 1)
        ob.data.materials.append(m)
        return ob

    def _text(name, body, size, m):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = body
        try:
            cu.font = bpy.data.fonts.load(
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf", check_existing=True)
        except (RuntimeError, OSError):
            pass
        cu.size = size
        cu.extrude = 0.002
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        ob = bpy.data.objects.new(name, cu)
        col.objects.link(ob)
        ob.data.materials.append(m)
        return ob

    def _pad(pid, bx, by, m):
        w, h, r, segs = 1.6, 1.2, 0.28, 8
        x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
        corners = [(x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, math.pi / 2),
                   (x0 + r, y0 + r, math.pi), (x1 - r, y0 + r, 3 * math.pi / 2)]
        verts = []
        for cx, cy, a0 in corners:
            for i in range(segs + 1):
                a = a0 + (i / segs) * (math.pi / 2)
                verts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
        me = bpy.data.meshes.new(f"p_station_{pid}_pad_me")
        me.from_pydata(verts, [], [tuple(range(len(verts)))])
        me.update()
        ob = bpy.data.objects.new(f"p_station_{pid}_pad", me)
        col.objects.link(ob)
        ob.location = (bx, by, 0.01)
        ob.data.materials.append(m)
        return ob

    def _pad_mat(pid, colhex):
        m = _mat(colhex, rough=0.8, metal=0.0, emit=0.0)
        try:
            m.blend_method = "BLEND"
        except (TypeError, AttributeError):
            pass
        try:
            m.shadow_method = "NONE"
        except (TypeError, AttributeError):
            pass
        try:
            b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            b.inputs["Alpha"].default_value = 0.35
        except (StopIteration, KeyError):
            pass
        return m

    # Nested three.js groups become empties; children are parented with local
    # offsets (lx, -lz, ly). The empty keeps the group's tilt with +rx about
    # Blender x (M Rx M^-1 = Rx): verified on Spark's lectern so the high edge
    # sits away from the character (+Y, toward the receiving zone).
    FZ = -0.45
    for pid in ids:
        if pid not in STATION_B:
            continue
        bx, by = STATION_B[pid]
        ccol = STATION_COL[pid]
        _pad(pid, bx, by, _pad_mat(pid, ccol))
        # Sign post and board; printed face on Blender -Y (three +z).
        sign_x = -0.95 if bx < 0 else 0.95
        sxw, syw = bx + sign_x, by - 0.12
        post = _cone(f"p_station_{pid}_signpost", 0.045, 0.035, 0.95,
                     _mat(0x3a3f44, rough=0.6, metal=0.3))
        _place(post, (sxw, syw, 0.475))
        board = box(f"p_station_{pid}_sign", (0.8, 0.04, 0.35), (sxw, syw, 0.925),
                    _mat("#0b1226", rough=0.6, metal=0.0))
        _move(board)
        border = box(f"p_station_{pid}_signborder", (0.86, 0.02, 0.41),
                     (sxw, syw + 0.012, 0.925),
                     _mat(ccol, rough=0.5, metal=0.0, emit=1.0))
        _move(border)
        tname = _text(f"p_station_{pid}_signname", STATION_NAME[pid], 0.11,
                      _mat("#ffffff", rough=0.5, metal=0.0, emit=2.5))
        tname.location = (sxw, syw - 0.023, 0.97)
        tname.rotation_euler = (math.radians(90), 0, 0)
        tjob = _text(f"p_station_{pid}_signjob", STATION_JOB[pid], 0.06,
                     _mat(ccol, rough=0.5, metal=0.0, emit=1.5))
        tjob.location = (sxw, syw - 0.023, 0.865)
        tjob.rotation_euler = (math.radians(90), 0, 0)

        if pid == "spark":
            wood = _mat(0x6b4f2e)
            topm = _mat(0x8a6134)
            papm = _mat(0xf8fafc, 0.9, 0)
            linm = _mat(0x94a3b8, 0.9, 0)
            bookm = _mat(0x7c4a21)
            clipm = _mat(0x9aa0a6, 0.4, 0.7)
            pagem = _mat(0xffffff, 0.9, 0)
            fy = by - FZ
            _move(box(f"p_station_spark_base", (0.5, 0.4, 0.06), (bx, fy, 0.03), wood))
            _move(box(f"p_station_spark_post", (0.12, 0.12, 0.95), (bx, fy, 0.53), wood))
            top = _empty(f"p_station_spark_top", (bx, fy, 1.02), (0.5, 0, 0))
            _parent(box(f"p_station_spark_lectern", (0.62, 0.46, 0.04), (0, 0, 0), topm),
                    top, (0, 0, 0))
            _parent(box(f"p_station_spark_lip", (0.62, 0.03, 0.05), (0, 0, 0), wood),
                    top, (0, -0.22, 0.02))
            _parent(box(f"p_station_spark_paper", (0.30, 0.40, 0.012), (0, 0, 0), papm),
                    top, (-0.14, 0, 0.028))
            for i in range(3):
                lz = -0.12 + i * 0.11
                _parent(box(f"p_station_spark_line{i}", (0.22, 0.028, 0.014), (0, 0, 0),
                            linm), top, (-0.14, -lz, 0.03))
            _parent(box(f"p_station_spark_book", (0.24, 0.32, 0.012), (0, 0, 0), bookm),
                    top, (0.17, -0.02, 0.028))
            _parent(box(f"p_station_spark_clip", (0.09, 0.045, 0.02), (0, 0, 0), clipm),
                    top, (0.17, 0.13, 0.035))
            piv = _empty(f"p_station_spark_pagepivot", (0.02, 0, 0.0385), (0, 0, 0),
                         parent=top)
            _parent(box(f"p_station_spark_page", (0.26, 0.36, 0.008), (0, 0, 0), pagem),
                    piv, (-0.13, 0, 0.004))
        elif pid == "sam":
            basem = _mat(0x2f3336)
            polem = _mat(0x3a3f44)
            monm = _mat(0x1c1f22, 0.6, 0.2)
            scrm = _mat("#0a1424", rough=0.5, metal=0.0, emit=1.5)
            strm = _mat("#38bdf8", rough=0.4, metal=0.0, emit=2.0)
            ledm = _emit_mat("p_station_sam_led_m", 0x052e16, 0x22ff55, 1.6, rough=0.5)
            fy, sy = by - FZ, by - (FZ + 0.037)
            _place(_cone(f"p_station_sam_base", 0.30, 0.26, 0.06, basem), (bx, fy, 0.03))
            _move(cyl(f"p_station_sam_pole", 0.04, 1.05, (bx, fy, 0.58), polem))
            _move(box(f"p_station_sam_monitor", (0.78, 0.07, 0.50), (bx, fy, 1.28), monm))
            _place(_plane(f"p_station_sam_screen", 0.70, 0.42, scrm), (bx, sy, 1.28),
                   (math.radians(90), 0, 0))
            boxes = [[70, 60, 90, 64], [175, 60, 90, 64], [280, 60, 90, 64],
                     [70, 140, 90, 64], [175, 140, 90, 64], [385, 140, 60, 64]]
            ys = sy - 0.002
            for i, (x, y, w, h) in enumerate(boxes):
                u = (x + w / 2) / 512.0
                v = 1.0 - (y + h / 2) / 320.0
                px, py = (u - 0.5) * 0.70, (v - 0.5) * 0.42
                ww, hh = w / 512.0 * 0.70, h / 320.0 * 0.42
                _move(box(f"p_station_sam_scr{i}t", (ww, 0.002, 0.006),
                          (bx + px, ys, 1.28 + py + hh / 2), strm))
                _move(box(f"p_station_sam_scr{i}b", (ww, 0.002, 0.006),
                          (bx + px, ys, 1.28 + py - hh / 2), strm))
                _move(box(f"p_station_sam_scr{i}l", (0.006, 0.002, hh),
                          (bx + px - ww / 2, ys, 1.28 + py), strm))
                _move(box(f"p_station_sam_scr{i}r", (0.006, 0.002, hh),
                          (bx + px + ww / 2, ys, 1.28 + py), strm))
            _move(box(f"p_station_sam_led", (0.05, 0.012, 0.025), (bx + 0.32, sy, 1.06),
                      ledm))
        elif pid == "kapi":
            basem = _mat(0x3a3f44)
            postm = _mat(0x52525b)
            housm = _mat(0xf2b705, 0.6, 0.2)
            xw, yw, yl = bx - 0.58, by + 0.23, by + 0.115
            _move(box(f"p_station_kapi_base", (0.34, 0.34, 0.08), (xw, yw, 0.04), basem))
            _move(box(f"p_station_kapi_post", (0.16, 0.16, 1.06), (xw, yw, 0.61), postm))
            _move(box(f"p_station_kapi_housing", (0.26, 0.22, 0.52), (xw, yw, 1.40), housm))
            for tag, colh, yy, emis in (("red", 0xff2222, 1.57, 0.3),
                                       ("amber", 0xffaa00, 1.40, 0.3),
                                       ("green", 0x22ff55, 1.23, 6.0)):
                lm = _emit_mat(f"p_station_kapi_lamp_{tag}_m", 0x111111, colh, emis,
                               rough=0.4)
                _place(_sphere(f"p_station_kapi_lamp_{tag}", 0.058, lm), (xw, yl, yy))
        elif pid == "wonder":
            deskm = _mat(0xb07a3f)
            sidem = _mat(0x8a6134)
            papm = _mat(0xf8fafc, 0.9, 0)
            penm = _mat(0x1d4ed8, 0.5, 0.2)
            fy = by - FZ
            _move(box(f"p_station_wonder_desk", (0.95, 0.50, 0.05), (bx, fy, 1.0), deskm))
            for s in (-1, 1):
                tag = "l" if s < 0 else "r"
                _move(box(f"p_station_wonder_side_{tag}", (0.05, 0.46, 1.0),
                          (bx + s * 0.45, fy, 0.5), sidem))
            _move(box(f"p_station_wonder_paper", (0.32, 0.42, 0.012),
                      (bx - 0.12, fy, 1.032), papm, rot_z=0.1))
            pen = cyl(f"p_station_wonder_pen", 0.012, 0.15, (bx + 0.22, by + 0.40, 1.04),
                      penm)
            _move(pen)
            pen.rotation_mode = "ZYX"
            pen.rotation_euler = (0, -math.pi / 2, 0.3)
        elif pid == "sef":
            basem = _mat(0x374151)
            bodym = _mat(0x4b5563)
            counm = _mat(0x1f2937, 0.6, 0.2)
            shelm = _mat(0x0b1226, 0.5, 0.3)
            scrm = _mat("#e8eef7", rough=0.5, metal=0.0, emit=1.0)
            tickm = _mat("#22c55e", rough=0.5, metal=0.0, emit=1.0)
            inkpm = _mat(0x7f1d1d)
            handm = _mat(0xc23b2e, 0.5, 0.1)
            papm = _mat(0xf8fafc, 0.9, 0)
            fy = by - FZ
            _move(box(f"p_station_sef_base", (0.56, 0.46, 0.08), (bx, fy, 0.04), basem))
            _move(box(f"p_station_sef_body", (0.50, 0.40, 1.00), (bx, fy, 0.58), bodym))
            top = _empty(f"p_station_sef_top", (bx, fy, 1.12), (0.35, 0, 0))
            _parent(box(f"p_station_sef_counter", (0.60, 0.50, 0.05), (0, 0, 0), counm),
                    top, (0, 0, 0))
            _parent(box(f"p_station_sef_tablet", (0.30, 0.22, 0.02), (0, 0, 0), shelm),
                    top, (-0.11, -0.02, 0.035))
            _parent(_plane(f"p_station_sef_screen", 0.26, 0.18, scrm),
                    top, (-0.11, -0.02, 0.047))
            pxy = []
            for cx, cy in ((34, 50), (56, 70), (96, 28)):
                u, v = cx / 128.0, 1.0 - cy / 96.0
                pxy.append(((u - 0.5) * 0.26, (v - 0.5) * 0.18))
            for i, (p0, p1) in enumerate(((pxy[0], pxy[1]), (pxy[1], pxy[2]))):
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                L, yaw = math.hypot(dx, dy), math.atan2(dy, dx)
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                _parent(box(f"p_station_sef_tick{i}", (L, 0.015, 0.002), (0, 0, 0), tickm),
                        top, (-0.11 + mx, -0.02 + my, 0.049), (0, 0, yaw))
            _parent(box(f"p_station_sef_inkpad", (0.12, 0.12, 0.03), (0, 0, 0), inkpm),
                    top, (0.19, -0.10, 0.04))
            head = _empty(f"p_station_sef_head", (0.19, -0.10, 0.0), (0, 0, 0), parent=top)
            _parent(cyl(f"p_station_sef_handle", 0.028, 0.10, (0, 0, 0), handm),
                    head, (0, 0, 0.10))
            _parent(_sphere(f"p_station_sef_knob", 0.035, handm), head, (0, 0, 0.16))
            _parent(box(f"p_station_sef_paper", (0.20, 0.16, 0.006), (0, 0, 0), papm),
                    top, (0.08, 0.15, 0.033))
        elif pid == "rover":
            deskm = _mat(0x9a8a6a)
            sidem = _mat(0x7a6c52)
            lapm = _mat(0x374151, 0.6, 0.2)
            shelm = _mat(0x1f2937, 0.6, 0.2)
            scrm = _mat("#101826", rough=0.5, metal=0.0, emit=1.0)
            headm = _mat("#0d9488", rough=0.5, metal=0.0, emit=1.5)
            papm = _mat(0xf8fafc, 0.9, 0)
            fy = by - FZ
            _move(box(f"p_station_rover_desk", (0.85, 0.60, 0.05), (bx, fy, 0.74), deskm))
            for s in (-1, 1):
                tag = "l" if s < 0 else "r"
                _move(box(f"p_station_rover_side_{tag}", (0.05, 0.56, 0.74),
                          (bx + s * 0.40, fy, 0.37), sidem))
            _move(box(f"p_station_rover_laptop", (0.36, 0.25, 0.025),
                      (bx - 0.16, by + 0.40, 0.778), lapm))
            lid = _empty(f"p_station_rover_lid", (bx - 0.16, by + 0.52, 0.79), (-0.32, 0, 0))
            _parent(box(f"p_station_rover_lidshell", (0.36, 0.02, 0.24), (0, 0, 0), shelm),
                    lid, (0, 0, 0.12))
            _parent(_plane(f"p_station_rover_screen", 0.32, 0.20, scrm),
                    lid, (0, -0.011, 0.12), (math.radians(90), 0, 0))
            hh, cy = 30.0 / 160.0 * 0.20, 0.12 + (0.10 - 30.0 / 160.0 * 0.20 / 2)
            _parent(box(f"p_station_rover_header", (0.32, 0.002, hh), (0, 0, 0), headm),
                    lid, (0, -0.012, cy))
            _move(box(f"p_station_rover_paper", (0.28, 0.38, 0.012),
                      (bx + 0.24, by + 0.42, 0.772), papm, rot_z=-0.12))
