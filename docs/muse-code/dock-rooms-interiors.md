# Muse Code task: furnish the rooms as Sena chose them

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Muse Image drew two concepts per room (`experiments/room_concepts.py`,
`experiments/mockups/room-<id>-<a|b>.png`); Sena picked one for each
(`experiments/mockups/room-choices.json`). The rooms built in the first pass
(`docs/muse-code/dock-rooms.md`) were sparse: a desk, a chair, a small screen in a 6 m room.
This pass furnishes the rooms chosen so far; the remaining ones follow in a second pass.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (you wrote `p_rooms`). Do not run commands or write probe
scripts: this run cannot approve them. Read the file, edit it directly, and stop; we build and
look at the scene ourselves.

Look at the chosen concept images before you start; they are the target:
`experiments/mockups/room-spark-a.png`, `room-sam-b.png`, `room-voice-b.png`,
`room-kapi-b.png`, `room-sef-b.png`, `room-wonder-b.png`, `room-ada-b.png`.

## Every room (all ten)

- Colour: today only part of the back wall is coloured and it looks washed out. Paint the
  whole back wall and both side walls inside each room in the character's colour (a rich matte
  version, not pastel), and the ceiling a light warm grey with a recessed light panel.
- The name plate above the glass: larger (about 1.6 m × 0.35 m), the name in bold white, lit,
  readable from the middle of the yard.
- Furnish the room so it looks lived-in across its width (6 m): the desk area in the middle,
  the character's things on both sides, something on every wall. Simple primitives in the
  scene's toy style (bevelled boxes, cylinders), real proportions.
- Keep the seat where it is (or update `rooms.json` if you move it): the character sits there
  facing the yard; nothing between the seat and the glass may be taller than 0.95 m, so the
  face stays visible. Keep the doorway clear.

## The seven chosen rooms

- **Spark (A)**: a calm reading desk: wooden desk with drawers, a desk lamp with a warm light,
  trays of delivery notes, a magnifier, a pen cup; a cork board on the back wall with pinned
  notes highlighted in yellow; sticky notes in orange; a side shelf with binders.
- **Sam (B)**: a calm lab: a camera on a tripod at one side, a small pallet with cartons as a
  model on the desk, a tally counter, pencil; carton drawings (white sheets with blue box
  outlines) pinned in a row on the back wall; a side table with a second camera.
- **Voice (B)**: a radio room: a wooden desk with a reel-to-reel tape recorder, a warm desk
  lamp, a notepad, headphones on the desk; notes pinned on the navy walls; a small speaker.
- **Kapı (B)**: a control room in cardboard: a big wall panel with three round lamps (red,
  amber, green, emissive) and knobs; a lectern with an open rule book; a cardboard desk with
  tape rolls and a clipboard; a red-and-white barrier pole leaning in a corner. On the rule
  book's pages, or as small plaques on the wall, Kapı's real twelve rules in their order:
  instruction, invisible text, unreadable, wrong product, hidden, damaged, disagree, receiver,
  readers disagree, audit, match, mismatch (numbered 1–12, short text).
- **Şef (B)**: a foreman's office: a walkie-talkie standing on the desk, a coffee thermos, a big
  red approval stamp on its pad, a stack of signed papers; a shift planner with coloured cards
  on the back wall; a hard hat on a hook.
- **Wonder (B)**: an old post office: pigeonhole shelves full of envelopes on a side wall, a
  typewriter on the desk, a rubber-stamp rack, a clipboard, a small plant and a yellow mug; a
  pinned map on the wall.
- **Ada (B)**: a maker lab: a whiteboard with diagram lines on one wall, a laptop on the desk,
  a small server rack with blinking green and blue lights (emissive), a teal neon sign "</>" on
  the back wall (emissive), a plant.

The other three (Iris, Glimmer, Rover) keep what they have for now.

## Checks we will run

- Build the polish scene and look at every room from the yard in Blender (rendered): the
  rooms read like the concepts, colourful and furnished, faces visible through the glass.
- Change nothing outside `experiments/blender/warehouse.py` (and `rooms.json` through it).
