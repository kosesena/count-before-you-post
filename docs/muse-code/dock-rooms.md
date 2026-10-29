# Muse Code task: a room for every character

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, playing the simulator: characters with nothing to do in the chosen delivery look like
they are just standing around. Her idea: give every character a room, on two storeys, in the warehouse; the
ones with no job in this delivery sit in their rooms and work, the ones with a job are out on
the floor ("this is very important"); make the warehouse bigger for it, redraw the inside if
needed; the rooms must stand against a wall, not in the middle of the hall. This task builds the rooms in the Blender scene; a second task moves the characters.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (you wrote its polish pass, `CBYP_POLISH=1`). Do not run
commands or write probe scripts: this run cannot approve them. Read the file, edit it directly,
and stop; we run Blender and the export ourselves.

## What to build (polish pass only)

Add `p_rooms(P)` and call it from `polish()`. The scene's axes: Blender metres, x across, y
toward the dock door (back wall at y = 10, dock door at x in [-1.7, 1.7]), the floor slab
`floor` spans x in [-15, 15], y in [-11, 15]; the roof and the left wall (x = -15) run over
y in [-11, 10]; the front (y = -11) and the right side are open today. Racks stand on the left
(x from -14 to -5, y from -7.5 to 8.5); the receiving zone is x in [-2.4, 2.4], y in [3.4, 7.6];
the quarantine zone x in [5, 9]; the forklift starts at (8, 0) and drives in the area between.

1. **Make the warehouse bigger toward the front**: extend the floor slab, the roof, ceiling,
   purlins and the left wall by 7 m to y = -18 (keep the epoxy floor material continuous;
   `p_shell` scales the left wall, so extend it there), and add high-bay lights over the new
   strip like the existing ones (`p_lights`). Close the front with a real **exterior wall** at
   y = -18 across the full width and height (the same panelled wall material, dark lower band
   and yellow stripe as the other walls, columns): the rooms are built against it, so they
   read as offices set into the building, not boxes standing in the hall. (The page's cameras
   are inside the hall, so the wall hides nothing they need.)
2. **Ten rooms on two storeys along the new front edge**: five rooms on the ground floor and
   five on an upper floor above them, each 6.0 m wide (x from -15 to 15) and 4.0 m deep
   (y from -18 to -13.5, their back walls against the exterior wall), 2.9 m tall per storey (upper floor level at z = 3.2). The upper
   floor has a **balcony** 1.6 m deep running its whole length in front of its rooms (y from
   -13.5 to -11.9), with a glass balustrade on a dark-steel frame, and a **staircase** at the
   right end (x about 13 to 15) from the ground-floor aisle up to the balcony, steel stairs with
   handrails. The side of every room facing the yard (y = -13.5) is **glass** with thin
   dark-steel mullions and an open doorway 1.0 m wide (no door leaf, so a character can walk in
   and out); the walls between rooms are pale panels; the back wall of each room is painted in
   the character's colour (a matte version), so from the yard the two rows read as ten
   colourful rooms behind glass. Keep a 2.5 m wide aisle in front of the ground-floor rooms
   clear (y from -13.5 to -11, under the balcony) with a yellow walkway line; the balcony must
   not hide the ground-floor rooms' faces from the yard (its slab is thin, about 0.2 m).
3. **Each room furnished for its character**, facing the yard so we see them through the glass:
   a desk 1.4 m wide with its long side parallel to the glass, about 1.2 m inside the glass;
   the chair behind it (between the desk and the back wall), so a seated character faces the
   yard; on the desk a **low** laptop or a monitor turned to the side so it does not hide the
   face; a few things that fit the character (Spark: a stack of delivery notes; Sam: a small
   camera on a tripod; Voice: headphones and a microphone; Kapı: a mini traffic light; Şef: a
   clipboard and a tablet; Wonder: a letter tray and a fountain pen; Ada: two monitors with
   code-green screens (both turned sideways); Iris: an easel with a canvas; Rover: a backpack
   and a thermos; Glimmer: a small glowing glass orb). Simple primitives in the scene's style.
4. **A name plate** above each room's glass, lit from inside: the character's name in white on
   a strip of its colour (Text object, the scene's font; the export turns text into meshes).
5. Room order, left to right (x = -15 → 15). Ground floor, the characters who work the dock
   most: Voice, Şef, Spark, Sam, Kapı. Upper floor: Ada, Iris, Glimmer, Wonder, Rover. Colours: Spark #f97316, Sam #3b82f6, Voice #1e3a8a, Kapı #a16207,
   Şef #1d4ed8, Wonder #ca8a04, Ada #0f766e, Iris #db2777, Rover #0d9488, Glimmer #8b5cf6.
6. A warm point light inside each room (no shadows), so the rooms glow softly.
7. Object names start with `p_room_<id>_` (ids: spark, sam, voice, kapi, sef, wonder, ada,
   iris, rover, glimmer), so the export keeps them static and joined per material.
8. Write `experiments/blender/out/rooms.json` when the polish scene is built: for every
   character `{ "floor": 0|1, "seat": [x, y], "seat_z": z, "face": yaw_degrees,
   "door": [x, y], "front": [x, y], "front_z": z }`: the chair's position and the seat's
   height, the direction a seated character faces (toward the yard, +y), the doorway's centre,
   and a point just outside the door (in the aisle, or on the balcony for the upper floor) with
   its floor height. Also `"stairs": [[x, y, z], ...]`: a walking path from the ground-floor
   aisle up the staircase to the balcony (a point every metre or so). Blender coordinates,
   metres.

Keep everything else as it is (the dock, the truck, the zones, the racks, the gate, the screen,
the forklift, the delivery), and keep the existing small office cabin. Nothing in the new
strip may block the forklift's area in the yard.

## Checks we will run

- Build the polish scene (`CBYP_POLISH=1 ... warehouse.py -- experiments/blender/out/polish ok`),
  render the overview cameras, export it with `experiments/web/export_dock.py`, and look at it
  in the simulator from the yard: ten rooms behind glass, readable name plates, furniture facing
  the yard.
- Change nothing outside `experiments/blender/warehouse.py`.
