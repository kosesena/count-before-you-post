"""LEGO-style outside of the dock's back wall (the `disari` view).

Builds the exterior face the outside camera sees: light-bluish-grey corrugated
cladding with a two-course brick plinth and a dark roof fascia, nine warm
roof-edge lamps, a thick black dock-door surround with a green traffic light, a
studded dark-bluish-grey baseplate apron with yellow dashed lane tiles and a
grey dock plate, and a clear 1 m square for a dock-guard minifig.
`warehouse.py` calls `build_lego_front` from `polish()`.
"""

import bpy
import math

# LEGO scale used here (factor 60 on a 4 cm minifigure).
STUD_PITCH = 0.48
STUD_R = 0.144
STUD_H = 0.10
PLATE_H = 0.192
BRICK_H = 0.576

BRICK_L = 1.92  # 4-stud brick length


def _lf_hex(h):
    """sRGB hex string to a linear-RGB tuple for Blender colours."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def _shade(rgb, f):
    """Scale a linear-RGB colour by `f`, clamped to [0, 1]."""
    return tuple(min(1.0, max(0.0, c * f)) for c in rgb)


def _gset(node, key, value):
    """Set a geometry-node input if it exists (Blender-version proof)."""
    try:
        node.inputs[key].default_value = value
    except (KeyError, TypeError, AttributeError, IndexError):
        pass


def build_lego_front(P, box, cyl, text, mat):
    """Build the LEGO facade, door frame and studded apron.

    `P` is the polish-materials dict, `box`/`cyl`/`text`/`mat` are the helpers
    from `experiments/blender/warehouse.py` (`P` and `text` are unused: the
    facade keeps LEGO colours and carries no lettering). Returns nothing.
    """
    grey = _lf_hex("#a0a5a9")  # light bluish grey
    dark = _lf_hex("#6c6e68")  # dark bluish grey
    Y0 = 10.15  # outer face of the back wall

    # --- 1. outer facade: panel, ribs, brick plinth, fascia ---
    panel_m = mat("p_lf_panel", grey, rough=0.6)
    rib_m = mat("p_lf_rib", _shade(grey, 1.07), rough=0.6)
    # Cladding panels; the dock opening (x in [-1.6, 1.6], z < 3.4) stays free.
    box("p_lf_panel_l", (13.4, 0.1, 7.0), (-8.3, Y0 + 0.05, 3.5), panel_m)
    box("p_lf_panel_r", (13.4, 0.1, 7.0), (8.3, Y0 + 0.05, 3.5), panel_m)
    box("p_lf_panel_top", (3.2, 0.1, 3.6), (0, Y0 + 0.05, 5.2), panel_m)
    # Vertical ribs every 0.24 m, from the plinth top (1.152) to the roof.
    PLINTH = 2 * BRICK_H
    k = 0
    x = -15.0 + 0.12
    while x < 15.0:
        if abs(x) < 1.6:  # over the door: only above the opening
            box(f"p_lf_rib{k}", (0.05, 0.08, 3.6), (x, Y0 + 0.14, 5.2), rib_m)
        else:
            h = 7.0 - PLINTH
            box(f"p_lf_rib{k}", (0.05, 0.08, h), (x, Y0 + 0.14, PLINTH + h / 2),
                rib_m)
        k += 1
        x += 0.24
    # Two-course plinth of 1.92 x 0.576 bricks in running bond.
    brick_a = mat("p_lf_brick_a", _shade(grey, 1.04), rough=0.55)
    brick_b = mat("p_lf_brick_b", _shade(grey, 0.96), rough=0.55)
    brick_d = mat("p_lf_brick_dark", dark, rough=0.55)
    n = 0
    for course in range(2):
        zc = BRICK_H / 2 + course * BRICK_H
        x = -15.0 + (course % 2) * (BRICK_L / 2) - BRICK_L
        while x < 15.0:
            for lo, hi in ((-15.0, -1.6), (1.6, 15.0)):
                a, b = max(x, lo), min(x + BRICK_L, hi)
                if b - a > 0.05:
                    if (n * 7 + course * 5) % 11 == 0:
                        m = brick_d
                    else:
                        m = brick_a if n % 2 == 0 else brick_b
                    box(f"p_lf_brick{course}_{n}", (b - a, 0.24, BRICK_H),
                        ((a + b) / 2, Y0 + 0.22, zc), m)
                    n += 1
            x += BRICK_L
    # Roof edge / fascia: 0.4 m tall, 0.3 m proud of the ribs.
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

    # --- 3. dock door frame + green traffic light ---
    for sgn in (-1, 1):
        box(f"p_lf_post{sgn}", (0.5, 0.4, 3.4), (sgn * 1.85, 10.35, 1.7),
            black_m)
    box("p_lf_header", (4.2, 0.4, 0.6), (0, 10.35, 3.7), black_m)
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

    # --- 4. studded apron: baseplate + instanced studs ---
    base_m = mat("p_lf_base", dark, rough=0.25)
    ap = bpy.data.objects.get("p_apron")
    if ap is not None:
        ap.data.materials.clear()
        ap.data.materials.append(base_m)
    # Studs on the STUD_PITCH grid over x in [-12, 12], y in [10.4, 29.6],
    # as instances (Mesh Grid -> Instance on Points, 16-sided cylinders).
    # The grid object sits at the grid centre (0, 20.0); stud centres are
    # STUD_H/2 above the apron top (z = -0.01). Studs under the 1 m minifig
    # square at (-4.0, 12.0) -- local (-4.0, -8.0) -- are deleted.
    nx, ny = 51, 41
    ng = bpy.data.node_groups.new("p_lf_studs", "GeometryNodeTree")
    try:
        ng.interface.new_socket(name="Geometry", in_out="INPUT",
                                socket_type="NodeSocketGeometry")
        ng.interface.new_socket(name="Geometry", in_out="OUTPUT",
                                socket_type="NodeSocketGeometry")
    except (TypeError, AttributeError):
        ng.inputs.new("NodeSocketGeometry", "Geometry")
        ng.outputs.new("NodeSocketGeometry", "Geometry")
    nodes, links = ng.nodes, ng.links
    out = nodes.new("NodeGroupOutput")
    grid = nodes.new("GeometryNodeMeshGrid")
    _gset(grid, "Vertices X", nx)
    _gset(grid, "Vertices Y", ny)
    _gset(grid, "Size X", (nx - 1) * STUD_PITCH)
    _gset(grid, "Size Y", (ny - 1) * STUD_PITCH)
    pos = nodes.new("GeometryNodeInputPosition")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(pos.outputs["Position"], sep.inputs["Vector"])

    def _lt(comp_out, center):
        sub = nodes.new("ShaderNodeMath")
        sub.operation = "SUBTRACT"
        links.new(comp_out, sub.inputs[0])
        sub.inputs[1].default_value = center
        ab = nodes.new("ShaderNodeMath")
        ab.operation = "ABSOLUTE"
        links.new(sub.outputs["Value"], ab.inputs[0])
        lt = nodes.new("ShaderNodeMath")
        lt.operation = "COMPARE"
        links.new(ab.outputs["Value"], lt.inputs[0])
        lt.inputs[1].default_value = 0.5
        lt.inputs[2].default_value = 0.02
        return lt.outputs["Value"]

    band = nodes.new("FunctionNodeBooleanMath")
    band.operation = "AND"
    links.new(_lt(sep.outputs["X"], -4.0), band.inputs[0])
    links.new(_lt(sep.outputs["Y"], -8.0), band.inputs[1])
    bnot = nodes.new("FunctionNodeBooleanMath")
    bnot.operation = "NOT"
    links.new(band.outputs["Boolean"], bnot.inputs[0])
    dele = nodes.new("GeometryNodeDeleteGeometry")
    try:
        dele.domain = "POINT"
    except (TypeError, AttributeError):
        pass
    try:
        dele.mode = "ALL"
    except (TypeError, AttributeError):
        pass
    links.new(grid.outputs["Mesh"], dele.inputs["Geometry"])
    links.new(bnot.outputs["Boolean"], dele.inputs["Selection"])
    stud = nodes.new("GeometryNodeMeshCylinder")
    _gset(stud, "Vertices", 16)
    _gset(stud, "Radius", STUD_R)
    _gset(stud, "Depth", STUD_H)
    inst = nodes.new("GeometryNodeInstanceOnPoints")
    links.new(dele.outputs["Geometry"], inst.inputs["Points"])
    links.new(stud.outputs["Mesh"], inst.inputs["Instance"])
    smat = nodes.new("GeometryNodeSetMaterial")
    _gset(smat, "Material", base_m)
    links.new(inst.outputs["Instances"], smat.inputs["Geometry"])
    links.new(smat.outputs["Geometry"], out.inputs["Geometry"])
    mesh = bpy.data.meshes.new("p_lego_apronstuds_mesh")
    ob = bpy.data.objects.new("p_lego_apronstuds", mesh)
    bpy.context.collection.objects.link(ob)
    ob.location = (0.0, 20.0, -0.01 + STUD_H / 2)
    ob.data.materials.append(base_m)
    mod = ob.modifiers.new("p_lf_studs", "NODES")
    mod.node_group = ng

    # --- 5. yellow dashed lane markings + grey dock plate ---
    # Tiles rest on the studs (stud tops at z = 0.09).
    yel_m = mat("p_lf_yellow", _lf_hex("#f2cd37"), rough=0.4)
    zc = 0.09 + 0.095
    for tag, x in (("l", -2.6), ("r", 2.6)):
        for d in range(7):  # 1.92 m tiles, 0.96 m gaps, y from 10.6 to 30
            box(f"p_lf_lane{tag}{d}", (0.48, 1.92, 0.19),
                (x, 11.56 + d * 2.88, zc), yel_m)
    plate_m = mat("p_lf_plate", grey, rough=0.4)
    box("p_lf_dockplate", (2.88, 0.96, 0.19), (0, 10.88, zc), plate_m)

    # --- 6. dock-guard minifig spot: the 1 m square at (-4.0, 12.0) stays
    # clear (its studs are deleted above); nothing is placed on it. ---
