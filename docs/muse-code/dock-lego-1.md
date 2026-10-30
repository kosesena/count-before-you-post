# Muse Code task: the warehouse built from LEGO (round 1: floor, walls, racks, cartons, plastic)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct: the cast are LEGO minifigures but the warehouse is generic low-poly; she saw
Muse Image's LEGO concepts (`experiments/mockups/lego-rooms.png`, `lego-hall.png`,
`lego-receiving.png`, `lego-outside.png`, on branch `claude/laughing-brattain-dd01bb`) and
said "this exactly". She also approved removing the old empty glass office. Round 2 will do
the forklift and the truck.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (the polished scene, `CBYP_POLISH=1`) and
`experiments/web/export_dock.py`. Do not run commands or write probe scripts: this run
cannot approve them. Read the files, edit them directly, and stop; we build, render and
export ourselves.

## Goal

Make the polished warehouse read as a **LEGO set** at the cast's scale, like the concepts:
a grey baseplate floor with visible studs, walls of grey bricks, LEGO-beam pallet racks,
cartons as bricks, everything glossy ABS plastic.

**Scale.** A real minifigure is ~4 cm; ours are 2.4 m, so the factor is 60. Use these
module constants and derive every LEGO dimension from them:
`STUD_PITCH = 0.48`, `STUD_R = 0.144`, `STUD_H = 0.10`, `PLATE_H = 0.192`,
`BRICK_H = 0.576`.

## 1. ABS plastic everywhere

Add a helper `lego_mat(name, hex)` that returns a Principled material with the colour,
roughness 0.22, specular/IOR of plastic (IOR 1.46), a very slight coat (coat weight 0.15,
coat roughness 0.1). Switch the polished build's main materials to it, keeping their
colours, in LEGO's palette where an obvious match exists: floor and walls light bluish grey
`#a0a5a9`, dark bluish grey `#6c6e68`, rack uprights blue `#0055bf`, beams orange `#fe8a18`,
yellow `#f2cd37`, red `#c91a09`, tan `#e4cd9e` (cartons), reddish brown `#582a12` (pallets,
table). Glass stays glass but as **trans-clear LEGO panels** (slight blue tint `#d6eef5`,
alpha 0.25, roughness 0.05). Emissive materials stay emissive.

## 2. Baseplate floor with studs

The hall floor becomes a light-bluish-grey baseplate (`PLATE_H` thick slab at the top of
the floor) covered in studs on the `STUD_PITCH` grid, over the whole interior floor
(x in [−14.8, 14.8], y in [−11.6, 9.8]; skip the studs under the receiving zone tape,
the quarantine hatching and the meeting rug, so tapes and rug lie flat). Build the studs as
**instances** of one cylinder mesh (r `STUD_R`, h `STUD_H`, 16 sides, a 0.01 bevel) via a
Geometry Nodes modifier (Mesh Grid → Instance on Points, with a delete-selection for the
skipped rectangles/circle), object name `p_lego_floorstuds`. The yellow and red floor
markings become flat **tiles** (`PLATE_H` thick boxes, glossy, no studs) on top of the
plate. Room floors and the balcony keep their finishes but get studs only along a 0.48 m
border inside the glass (a row of studs, not the whole floor).

## 3. Brick walls

The left, back and front walls (and the outer face of the room block's end walls) show
**brick courses**: generate, in Python with `bpy.data.images.new` and pixel arrays, a
1024×1024 tileable image of running-bond 2x4 bricks (1.92 m × 0.576 m at the scale above,
a 0.02 m dark grey mortar line, each brick's grey jittered ±4 %, about 6 % of bricks dark
bluish grey and 2 % medium blue `#5a93db`, as in `lego-receiving.png`), pack it into the
blend (`image.pack()`), and use it as the base colour of the wall material with box/UV
mapping scaled so one tile spans 4 bricks across and 4 courses up. Add a matching normal
map image the same way (bevelled brick edges) so Cycles shows relief. The images are packed,
so the glTF export carries them.

## 4. LEGO pallet racks

In `p_racks` (racks are against the walls now — keep the layout): uprights as blue
**1x1 brick columns** (square 0.48 section with a stud on top), beams as orange **1x2 plates
/ technic beams** (0.48 deep, `PLATE_H` thick, a row of studs on top), shelf decks as
light-grey plates with studs. Keep the loaded pallets.

## 5. Cartons as bricks

Every carton/box in the polished scene (racks, props, the stacks by the door, the delivery
on the pallet) becomes a **tan brick**: same footprint as now, glossy tan, a stud on top for
every `STUD_PITCH` cell its top covers (at least one, centred), and a thin darker tape line
across the top. Keep the delivery's carton count and positions exactly (the simulator and
the truth files depend on them); only their look changes. Pallets become reddish-brown
plates with slats.

## 6. The meeting table and stools

Keep the Meshy models; add studs on the table top (on the pitch grid inside the radius,
leaving a 0.3 m clear ring at the edge and the props' spots), reddish-brown table material
tint, and a stud on each stool seat.

## 7. Remove the old glass office

Delete `p_office` (the empty glass office at the right, `p_of_*` objects and its light)
and its call; nothing else depends on it (check).

## 8. Export

`export_dock.py` must **realize geometry-node instances** before joining meshes (apply the
`p_lego_floorstuds` modifier: `object.modifier_apply` or `bpy.ops.object.duplicates_make_real`
after converting to mesh), keep the packed brick images as glTF textures, and stay Draco
compressed. Keep its exclusions (cameras, lights, `p_stand_`, `p_station_`).

## Keep

The layout (rooms, stations, table at (1.0, −7.0), zone, quarantine, door, racks against the
walls), every object name prefix the simulator relies on (`p_`, `zone_`, `screen_`,
`gate_`, `pallet`, `p_rk*`, `p_meet_*`, `p_room_<id>_*`), `rooms.json`, the delivery's
cartons. Change nothing outside these two files.
