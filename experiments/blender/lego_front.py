"""LEGO-style outside of the dock's back wall (the `disari` view).

Builds the exterior face the outside camera sees: the hall's small-brick
texture over the whole outer facade, a dark roof fascia, nine warm roof-edge
lamps, a thick black dock-door surround with a yellow MAL KABUL 01 sign and
a traffic light, flat yellow dashed lane tiles and a grey dock plate on the
dark stud-textured apron (warehouse.py owns the apron material), and a clear
1 m square for a dock-guard minifig.
`warehouse.py` calls `build_lego_front` from `polish()`.
"""

import bpy
import math

# LEGO scale used here (factor 60 on a 4 cm minifigure).
STUD_PITCH = 0.48
LF_BRICK_L = 0.96   # facade bricks: 1x4 at our scale, in running bond
LF_BRICK_H = 0.288


def _lf_hex(h):
    """sRGB hex string to a linear-RGB tuple for Blender colours."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def _lf_brick_uvs(ob):
    """Box-projected world-scale UVs: one brick tile per 4 bricks x 4 courses,
    the same scale as the hall walls inside (warehouse.py)."""
    tile_w, tile_h = 4 * LF_BRICK_L, 4 * LF_BRICK_H
    mesh = ob.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active
    sx, sy, sz = ob.scale
    ox, oy, oz = ob.location
    for poly in mesh.polygons:
        n = poly.normal
        ax = 0 if abs(n.x) >= abs(n.y) and abs(n.x) >= abs(n.z) else \
            (1 if abs(n.y) >= abs(n.z) else 2)
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            x, y, z = co[0] * sx + ox, co[1] * sy + oy, co[2] * sz + oz
            if ax == 0:
                u, v = y / tile_w, z / tile_h
            elif ax == 1:
                u, v = x / tile_w, z / tile_h
            else:
                u, v = x / tile_w, y / tile_w
            uv.data[li].uv = (u, v)


def build_lego_front(P, box, cyl, text, mat):
    """Build the LEGO facade, door frame, sign and lane tiles.

    `P` is the polish-materials dict (`P["wall_back"]` is the hall's small
    white brick texture, reused here at the same scale), `box`/`cyl`/`text`/
    `mat` are the helpers from `experiments/blender/warehouse.py` (`text`
    draws the door sign). Returns nothing.
    """
    grey = _lf_hex("#a0a5a9")  # light bluish grey
    dark = _lf_hex("#6c6e68")  # dark bluish grey
    Y0 = 10.15  # outer face of the back wall

    # --- 1. brick facade: the hall's small white brick texture everywhere.
    # Three slabs with P["wall_back"] at the inside scale (0.96 x 0.288
    # running bond, faint mortar, normal-map relief); the dock opening
    # (x in [-1.6, 1.6], z < 3.4) stays free. No scattered brick boxes.
    for _fname, _fdims, _floc in (
            ("p_lf_facade_l", (13.4, 0.24, 7.0), (-8.3, Y0 + 0.22, 3.5)),
            ("p_lf_facade_r", (13.4, 0.24, 7.0), (8.3, Y0 + 0.22, 3.5)),
            ("p_lf_facade_top", (3.2, 0.24, 3.6), (0, Y0 + 0.22, 5.2))):
        _lf_brick_uvs(box(_fname, _fdims, _floc, P["wall_back"]))
    # Roof edge / fascia: 0.4 m tall, 0.3 m proud of the facade.
    fascia_m = mat("p_lf_fascia", dark, rough=0.6)
    box("p_lf_fascia", (30.0, 0.45, 0.4), (0, 10.4, 7.0), fascia_m)

    # --- 2. roof-edge lights: 9 warm lamps + one 40 W point light each ---
    black_m = mat("p_lf_black", (0.02, 0.02, 0.02), rough=0.8)
    warm_m = mat("p_lf_lampwarm", _lf_hex("#ffd9a0"), emit=6.0)
    for k in range(9):
        x = -12.0 + k * 3.0
        box(f"p_lf_roof{k}", (0.3, 0.25, 0.15), (x, 10.55, 6.7), black_m)
        cyl(f"p_lf_roofdisc{k}", 0.09, 0.03, (x, 10.55, 6.61), warm_m)
        bpy.ops.object.light_add(type="POINT", location=(x, 10.6, 6.4))
        L = bpy.context.object
        L.name = f"p_lf_rooflight{k}"
        L.data.energy = 40
        L.data.color = _lf_hex("#ffd9a0")

    # --- 3. dock door frame + yellow sign + traffic light ---
    for sgn in (-1, 1):
        box(f"p_lf_post{sgn}", (0.5, 0.4, 3.4), (sgn * 1.85, 10.35, 1.7),
            black_m)
    box("p_lf_header", (4.2, 0.4, 0.6), (0, 10.35, 3.7), black_m)
    sign_m = mat("p_lf_sign", _lf_hex("#f2cd37"), rough=0.4)
    box("p_lf_sign", (2.8, 0.05, 0.42), (0, 10.56, 3.7), sign_m)
    text("p_lf_signtxt", "MAL KABUL 01", (0, 10.59, 3.7), 0.26, black_m,
         rot=(math.radians(90), 0, math.radians(180)))
    tx, ty = -3.2, 10.7  # left of the door, outside
    box("p_lf_sigpost", (0.12, 0.12, 1.7), (tx, ty, 0.85), black_m)
    box("p_lf_sighousing", (0.48, 0.4, 1.2), (tx, ty, 2.3), black_m)
    sig_red = mat("p_lf_sigred", (0.25, 0.02, 0.02), rough=0.3)
    sig_amber = mat("p_lf_sigamber", (0.30, 0.14, 0.0), rough=0.3)
    sig_green = mat("p_lf_siggreen", (0.05, 1, 0.2), rough=0.3, emit=8.0)
    for name, dz, m in (("red", 0.38, sig_red), ("amber", 0.0, sig_amber),
                        ("green", -0.38, sig_green)):
        cyl(f"p_lf_sig_{name}", 0.11, 0.05, (tx, ty + 0.2, 2.3 + dz), m,
            rot=(math.radians(90), 0, 0))

    # --- 4. flat yellow dashed lane tiles + grey dock plate on the apron ---
    # The apron top is at z = -0.01 (warehouse.py owns its stud texture);
    # the tiles are 0.03 m thick plates lying on it.
    yel_m = mat("p_lf_yellow", _lf_hex("#f2cd37"), rough=0.4)
    for tag, x in (("l", -2.6), ("r", 2.6)):
        for d in range(7):  # 1.92 m tiles, 0.96 m gaps, y from 10.6 to 30
            box(f"p_lf_lane{tag}{d}", (STUD_PITCH, 1.92, 0.03),
                (x, 11.56 + d * 2.88, 0.005), yel_m)
    plate_m = mat("p_lf_plate", grey, rough=0.4)
    box("p_lf_dockplate", (2.88, 0.96, 0.03), (0, 10.88, 0.005), plate_m)

    # --- 5. dock-guard minifig spot: the 1 m square at (-4.0, 12.0) stays
    # clear of lane tiles (the apron studs are a texture now). ---
