"""Render synthetic receiving-dock scenes with a known number of boxes.

Run headless (does not touch any open Blender file):
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
      -P experiments/blender/scenes.py -- experiments/blender/out

Writes <name>.png and truth.json (boxes on the belt, distractors) into the output dir.
"""
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler

BELT_W, BELT_L = 1.4, 6.0  # metres; belt runs along X

# name: (boxes on belt, layout, distractors, seed)
SCENES = {
    "s01-duzenli-12": (12, "row", 0, 1),
    "s02-daginik-20": (20, "clutter", 8, 2),
}


def material(name, color, rough=0.8, noise=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = rough
    if noise:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 40.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = [c * (1 - noise) for c in color[:3]] + [1]
        ramp.color_ramp.elements[1].color = [min(1, c * (1 + noise)) for c in color[:3]] + [1]
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = color
    return mat


def cube(name, size, loc, rot=(0, 0, 0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    if mat:
        ob.data.materials.append(mat)
    bevel = ob.modifiers.new("bevel", "BEVEL")
    bevel.width, bevel.segments = 0.006, 2
    return ob


def cardboard_box(i, loc, yaw, rnd, mats):
    sx, sy, sz = rnd.uniform(0.25, 0.45), rnd.uniform(0.2, 0.35), rnd.uniform(0.15, 0.35)
    z = loc[2] + sz / 2
    box = cube(f"box_{i}", (sx, sy, sz), (loc[0], loc[1], z), (0, 0, yaw), rnd.choice(mats["card"]))
    # Packing tape along the top.
    cube(f"tape_{i}", (sx * 1.01, 0.05, 0.004), (loc[0], loc[1], z + sz / 2), (0, 0, yaw),
         mats["tape"])
    if rnd.random() < 0.6:  # shipping label
        cube(f"label_{i}", (0.1, 0.07, 0.003),
             (loc[0] + 0.05 * math.cos(yaw), loc[1] + 0.05 * math.sin(yaw), z + sz / 2 + 0.003),
             (0, 0, yaw + 0.1), mats["label"])
    return box, (sx, sy)


def distractor(i, loc, rnd, mats):
    """Things on a dock belt that are not cardboard boxes: poly mailers, a plastic crate."""
    yaw = rnd.uniform(0, math.pi)
    if rnd.random() < 0.7:
        # Soft, wrinkled mailer: rounded, puffy, noisy surface.
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24,
                                             location=(loc[0], loc[1], 0.04))
        ob = bpy.context.object
        ob.name = f"bag_{i}"
        ob.scale = (rnd.uniform(0.2, 0.26), rnd.uniform(0.14, 0.18), 0.045)
        ob.rotation_euler = (0, 0, yaw)
        ob.data.materials.append(rnd.choice(mats["bag"]))
        tex = bpy.data.textures.new(f"wrinkle_{i}", "CLOUDS")
        tex.noise_scale = 0.05
        disp = ob.modifiers.new("wrinkle", "DISPLACE")
        disp.texture, disp.strength = tex, 0.25
        bpy.ops.object.shade_smooth()
        return ob
    # Open plastic crate: floor and four thin walls.
    w, d, h, t = 0.42, 0.3, 0.14, 0.015
    c, s = math.cos(yaw), math.sin(yaw)
    parts = [((w, d, t), (0, 0, t / 2)), ((w, t, h), (0, d / 2, h / 2)),
             ((w, t, h), (0, -d / 2, h / 2)), ((t, d, h), (w / 2, 0, h / 2)),
             ((t, d, h), (-w / 2, 0, h / 2))]
    for k, (size, (ox, oy, oz)) in enumerate(parts):
        cube(f"crate_{i}_{k}", size, (loc[0] + ox * c - oy * s, loc[1] + ox * s + oy * c, oz),
             (0, 0, yaw), mats["crate"])


def build(n_boxes, layout, n_distract, seed):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rnd = random.Random(seed)
    mats = {
        "card": [material(f"card{k}", (0.55 + d, 0.38 + d, 0.22 + d / 2, 1), noise=0.08)
                 for k, d in enumerate((-0.05, 0.0, 0.05))],
        "tape": material("tape", (0.75, 0.6, 0.4, 1), rough=0.3),
        "label": material("label", (0.95, 0.95, 0.93, 1)),
        "bag": [material("bag_black", (0.03, 0.03, 0.035, 1), rough=0.25),
                material("bag_grey", (0.6, 0.62, 0.65, 1), rough=0.35)],
        "crate": material("crate", (0.05, 0.25, 0.75, 1), rough=0.5),
        "belt": material("belt", (0.12, 0.12, 0.13, 1), noise=0.15),
        "rail": material("rail", (0.08, 0.2, 0.6, 1), rough=0.4),
        "floor": material("floor", (0.45, 0.45, 0.43, 1), noise=0.1),
    }
    cube("floor", (20, 20, 0.02), (0, 0, -0.75), mat=mats["floor"])
    cube("belt", (BELT_L, BELT_W, 0.04), (0, 0, -0.02), mat=mats["belt"])
    for side in (-1, 1):
        cube(f"rail_{side}", (BELT_L, 0.08, 0.7), (0, side * (BELT_W / 2 + 0.04), -0.3),
             mat=mats["rail"])

    placed = []

    def free(x, y, r):
        return all(math.hypot(x - px, y - py) > r + pr for px, py, pr in placed)

    count = 0
    if layout == "row":
        xs = [(-BELT_L / 2 + 0.4) + k * (BELT_L - 0.8) / max(1, n_boxes - 1)
              for k in range(n_boxes)]
        for k, x in enumerate(xs):
            y = 0.25 * (1 if k % 2 else -1)
            cardboard_box(k, (x, y, 0.0), rnd.uniform(-0.15, 0.15), rnd, mats)
            count += 1
    else:
        tries = 0
        while count < n_boxes and tries < 5000:
            tries += 1
            x = rnd.uniform(-BELT_L / 2 + 0.3, BELT_L / 2 - 0.3)
            y = rnd.uniform(-BELT_W / 2 + 0.22, BELT_W / 2 - 0.22)
            if free(x, y, 0.2):  # boxes may touch each other, never overlap
                cardboard_box(count, (x, y, 0.0), rnd.uniform(0, math.pi), rnd, mats)
                placed.append((x, y, 0.2))
                count += 1
        for k in range(n_distract):
            for _ in range(500):
                x = rnd.uniform(-BELT_L / 2 + 0.3, BELT_L / 2 - 0.3)
                y = rnd.uniform(-BELT_W / 2 + 0.2, BELT_W / 2 - 0.2)
                if free(x, y, 0.18):
                    distractor(k, (x, y, 0), rnd, mats)
                    placed.append((x, y, 0.18))
                    break

    # Dock camera: above the belt, looking down at an angle.
    bpy.ops.object.camera_add(location=(0, -3.6, 3.4), rotation=Euler((math.radians(47), 0, 0)))
    cam = bpy.context.object
    cam.data.lens = 24
    bpy.context.scene.camera = cam
    bpy.ops.object.light_add(type="AREA", location=(0, -1, 4))
    key = bpy.context.object
    key.data.energy, key.data.size = 900, 4
    bpy.ops.object.light_add(type="SUN", location=(3, 3, 5), rotation=(0.6, 0.3, 0.8))
    bpy.context.object.data.energy = 2.0
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.35, 0.37, 1)
    bpy.context.scene.world = world
    return count


def render(path):
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    truth = {}
    for name, (n, layout, n_distract, seed) in SCENES.items():
        boxes = build(n, layout, n_distract, seed)
        render(out / f"{name}.png")
        truth[name] = {"boxes_on_belt": boxes, "distractors": n_distract, "layout": layout,
                       "seed": seed}
        print(name, truth[name])
    (out / "truth.json").write_text(json.dumps(truth, indent=2))
