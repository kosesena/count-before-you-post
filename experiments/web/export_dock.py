"""Export the dressed-up dock for the browser simulator, as one light GLB.

Usage: blender -b experiments/blender/out/polish/depo-ok.blend \
           -P experiments/web/export_dock.py -- <out.glb>
       blender -b experiments/blender/out/depo-<case>.blend \
           -P experiments/web/export_dock.py -- <out.glb> delivery
The second form writes only that case's delivery (pallet, cartons, labels), as measured: the
page loads the one the player picked. The first also writes <out>.colliders.json: the floor
footprint of everything a forklift can hit, as [x0, y0, x1, y1] boxes in Blender metres.

From the saved polish scene: standees, cameras and lights go (the page lights the scene
itself), text objects become meshes, the removed stud instancers are dropped, and any
still-procedural material (floor, walls) is baked to a 2K texture so it looks the same
outside Blender; the packed stud/brick images stay as the glTF textures. The parts the player
touches stay separate nodes, named for the page:
  forklift   every p_fl_* part (the page drives it and moves its forks)
  delivery   the pallet with its cartons and labels (picked up by the forks)
  jack       the pallet jack under it
  gate       gate pole, housing, light and barrier (the light changes colour)
  screen     the decision screen
Everything else is static and joined per material, so the page draws a few dozen meshes
instead of 1,600. Draco-compressed, WebP textures. Prints sizes and node names.
"""
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
out = Path(ARGS[0]).resolve()
DELIVERY_ONLY = len(ARGS) > 1 and ARGS[1] == "delivery"
BAKE = ("p_floor", "p_wall_back", "p_wall_side", "p_apron", "p_ceil")
GROUPS = {"forklift": ("p_fl_",), "jack": ("jack_",), "gate": ("gate_", "barrier_"),
          "screen": ("screen_",)}
PALLET, REACH = Vector((0.0, 5.5)), 1.1   # the delivery: anything on the pallet's footprint


def log(msg):
    print("[export_dock]", msg, flush=True)


def group_of(ob):
    for g, prefixes in GROUPS.items():
        if ob.name.startswith(prefixes):
            return g
    x, y = ob.matrix_world.translation.x, ob.matrix_world.translation.y
    if (Vector((x, y)) - PALLET).length < REACH and ob.matrix_world.translation.z < 1.6:
        return "delivery"
    return None


def drop_stud_instancers():
    """Drop the removed stud instancers (floor, apron) and the stud template, if
    an older scene still has them; new scenes carry studs as textures only."""
    for name in ("p_lego_floorstuds", "p_lego_apronstuds", "p_lego_stud_template"):
        ob = bpy.data.objects.get(name)
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
            log(f"dropped {name}")


def clean():
    drop_stud_instancers()
    for ob in list(bpy.data.objects):
        if ob.type in ("CAMERA", "LIGHT") or ob.name.startswith(("p_stand_", "p_standft_", "p_station_")):
            bpy.data.objects.remove(ob, do_unlink=True)
    fonts = [o for o in bpy.data.objects if o.type == "FONT"]
    for ob in fonts:
        with bpy.context.temp_override(active_object=ob, selected_objects=[ob],
                                       selected_editable_objects=[ob], object=ob):
            bpy.ops.object.convert(target="MESH")
    log(f"{len(fonts)} text objects to meshes")
    # Parented props (a rule book on its lectern) are joined by material later: free them
    # first, keeping where they are, or they land at their local offset from the origin.
    for ob in bpy.data.objects:
        if ob.parent is not None and ob.parent.type != "ARMATURE":
            mw = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = mw
    for ob in bpy.data.objects:   # modifiers (solidify, bevel) baked into the meshes
        if ob.type == "MESH" and ob.modifiers:
            with bpy.context.temp_override(active_object=ob, selected_objects=[ob],
                                           selected_editable_objects=[ob], object=ob):
                bpy.ops.object.convert(target="MESH")


def bake_procedural(size=2048):
    """Bake each procedural material's colour into an image and rewire it to that image."""
    scene = bpy.context.scene
    try:
        scene.render.engine = "CYCLES"
    except TypeError as e:
        raise SystemExit(f"Cycles needed for baking: {e}")
    scene.cycles.samples = 16
    for mname in BAKE:
        m = bpy.data.materials.get(mname)
        if not m:
            continue
        bsdf0 = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
                     None)
        links0 = bsdf0.inputs["Base Color"].links if bsdf0 is not None else []
        if not links0:
            log(f"not baking {mname}: flat colour, nothing to bake")
            continue
        if any(l.from_node.type == "TEX_IMAGE" for l in links0):
            for l in links0:  # packed brick images stay as the glTF textures
                if l.from_node.type == "TEX_IMAGE" and l.from_node.image:
                    l.from_node.image.pack()
            log(f"not baking {mname}: keeping packed textures")
            continue
        users = [o for o in bpy.data.objects if o.type == "MESH" and m.name in [s.name for s in o.data.materials if s]]
        img = bpy.data.images.new(f"bake_{mname}", size, size)
        nt = m.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.nodes.active = tex
        for ob in users:
            if not ob.data.uv_layers:
                with bpy.context.temp_override(active_object=ob, selected_objects=[ob],
                                               selected_editable_objects=[ob], object=ob):
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.uv.smart_project(island_margin=0.01)
                    bpy.ops.object.mode_set(mode="OBJECT")
        with bpy.context.temp_override(active_object=users[0], selected_objects=users,
                                       selected_editable_objects=users, object=users[0]):
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        for link in list(bsdf.inputs["Base Color"].links):
            nt.links.remove(link)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        img.pack()
        log(f"baked {mname} on {len(users)} object(s)")


def join(obs, name):
    obs = [o for o in obs if o.type == "MESH"]
    if not obs:
        return None
    for o in obs:   # world transforms into the mesh, parents dropped, before joining
        o.parent = None
    with bpy.context.temp_override(active_object=obs[0], selected_objects=obs,
                                   selected_editable_objects=obs, object=obs[0]):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if len(obs) > 1:
            bpy.ops.object.join()
    obs[0].name = name
    return obs[0]


def group_and_join():
    groups, static = defaultdict(list), defaultdict(list)
    for ob in [o for o in bpy.data.objects if o.type == "MESH"]:
        g = group_of(ob)
        if g:
            groups[g].append(ob)
        else:
            mat = ob.data.materials[0].name if ob.data.materials and ob.data.materials[0] else "none"
            static[mat].append(ob)
    for g, obs in groups.items():
        # The forklift moves as one body; its forks are kept apart so the page can lift them.
        if g == "forklift":
            forks = [o for o in obs if o.name.startswith(("p_fl_fork", "p_fl_mast_in", "p_fl_carriage"))]
            join(forks, "forklift_forks")
            obs = [o for o in obs if o not in forks]
        join(obs, g)
        log(f"node {g}: {len(obs)} parts")
    for mat, obs in static.items():
        join(obs, f"static_{mat}")
    log(f"static: {len(static)} meshes by material")


def colliders():
    """Floor footprints of solid things (on the floor, taller than 0.3 m, not the floor or
    the roof), before anything is joined. The delivery, forklift and jack move: not here."""
    boxes = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or group_of(ob) in ("delivery", "forklift", "jack"):
            continue
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
        y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
        z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
        if z0 > 0.3 or z1 - z0 < 0.3 or (x1 - x0) * (y1 - y0) > 60:
            continue
        boxes.append([round(v, 2) for v in (x0, y0, x1, y1)])
    return boxes


def delivery_only():
    for ob in list(bpy.data.objects):
        if ob.type == "FONT" and group_of(ob) == "delivery":
            with bpy.context.temp_override(active_object=ob, selected_objects=[ob],
                                           selected_editable_objects=[ob], object=ob):
                bpy.ops.object.convert(target="MESH")
    keep = [o for o in bpy.data.objects if o.type == "MESH" and group_of(o) == "delivery"]
    for ob in list(bpy.data.objects):
        if ob not in keep:
            bpy.data.objects.remove(ob, do_unlink=True)
    join(keep, "delivery")
    log(f"delivery: {len(keep)} parts")


bpy.ops.object.select_all(action="DESELECT")
if DELIVERY_ONLY:
    delivery_only()
else:
    import json
    clean()
    boxes = colliders()
    Path(str(out) + ".colliders.json").write_text(json.dumps(boxes))
    log(f"{len(boxes)} colliders")
    bake_procedural()
    group_and_join()
bpy.ops.export_scene.gltf(
    filepath=str(out), export_format="GLB", export_apply=True, export_animations=False, export_lights=False,
    export_cameras=False, export_image_format="WEBP", export_image_quality=90,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
names = sorted(o.name for o in bpy.data.objects if o.type == "MESH")
log(f"wrote {out} {out.stat().st_size / 1e6:.2f} MB, {len(names)} meshes")
log("nodes " + ", ".join(n for n in names if not n.startswith("static_")))
