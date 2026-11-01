# Muse Code task: Brick Dock rooms, round 1 (ground floor)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 1 Nov: in the LEGO simulator the ten offices are still one template (same desk, monitor,
bookcase, chair and plant; only the colour and the name differ). Each should feel like its
agent, using the room concepts Sena already chose for the Blender dock
(`docs/muse-code/dock-rooms-signature-1.md` to `-4.md`). This round does the five ground-floor
rooms; a second round does the upper five.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator
`site/sim-lego/main.js` (three.js). The ten offices are built in one loop, `for(let floor=0;
floor<2;floor++)for(let n=0;n<5;n++){ ... }` (around lines 160-185). Floor 0 holds Spark, Şef,
Sam, Voice and Kapı. Make each of these five rooms its own place, in LEGO bricks, readable from
the warehouse floor and from the "rooms" camera view. Leave the upper five rooms (Iris, Ada,
Glimmer, Wonder, Rover) exactly as they are.

Room-local frame (inside the loop, `room` group): x runs across the room from -2.175 to +2.175,
z runs from the back wall (-2.5) to the glass front (+2.58), y is up from the floor (0.16).
The glass front, the door (local x about 0.1 to 2.08), the name sign (`litName`), the room
number label on the back wall, the room's `roomLight` and the seated figure at (-0.65, 0.18,
0.05) must stay. Keep a clear walking lane at local x 1.6 to 2.1, z -0.6 to 2.6 (the agent walks
out through the door there) and keep the chair where the figure sits.

What each room should become (adapted from the chosen concepts; use the existing helpers
`box`, `cyl`, `label`, `sheet`, `plant`, and colours from `C`):

- **Spark** (orange): a cosy reading office. A large cork board on the back wall crowded with
  small white checklists and orange/yellow sticky notes; a wooden desk with a drawer pedestal; a
  black anglepoise desk lamp; a magnifying glass, a clipboard, a pen cup; an orange chair.
- **Şef** (royal blue): a tidy supervisor's booth. A shift planner on the back wall (a cork
  board with a 3×4 grid of coloured cards); a walkie-talkie in a wall cradle; a grey steel
  counter instead of the wooden desk, with a big red-and-black rubber stamp, stacked forms and a
  steel thermos; a hard hat and a hi-vis vest on wall hooks.
- **Sam** (light blue): a clean counting studio. A neat grid of carton drawings on the back wall
  (white sheets with a simple box outline, 2 rows × 5); a white desk; a camera on a tall tripod
  pointed at the desk; a mini pallet with a small stack of mini cartons on the desk; a flip
  counter showing digits. Mostly white, minimal.
- **Voice** (deep navy): a warm, dim listening room. Padded acoustic squares on the back wall;
  scattered sticky notes; a dark wooden desk; a big reel-to-reel tape recorder with two large
  reels clearly visible; a desk lamp with a cream shade; headphones; an old desk phone. No
  bookcase.
- **Kapı** (cardboard): everything made of cardboard. Back and side walls clad in brown
  cardboard panels with packing-tape strips; a cardboard box desk with a tape roll; a three-lamp
  signal panel on the back wall (red, amber, green; green lit); a big open rule book on a
  cardboard lectern; a red-and-white striped barrier post near the front.

Drop the shared bookcase, monitor and plant in these five rooms where they do not fit the
concept (keep a monitor only if the concept has one). Signature pieces must be large enough to
read from across the warehouse. LEGO look: chunky boxes and cylinders, studs on large flat tops
where the helpers allow it, no fine detail that turns into noise.

Performance: no new lights (you may change the colour or intensity of each room's existing
`roomLight` to fit its mood), no new textures over 256 px, keep each room under about 70 new
`box`/`cyl` calls, and call `flush(room)` as now. Emissive bits (Kapı's green lamp, Spark's
lamp, Voice's lamp) may use `toneMapped:false` materials, kept soft.

Change only `site/sim-lego/main.js`, only inside the office loop (you may add small helper
functions right above it). Do not move or resize the rooms, walls, balcony, doors or anything
outside the loop; do not touch routes, collision or UI; do not change `?v=` strings.

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we check it in the browser and measure the frame rate ourselves.
