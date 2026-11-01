# Muse Code task: Brick Dock meeting table

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 1 Nov: on the big orange meeting table there are only two sheets, a dark tablet and a
black block with a grey rod that reads like a single button. It should look like the table
where the team meets about a delivery.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator
`site/sim-lego/main.js` (three.js). The meeting island is built around lines 259-270: a navy
disk, an orange tiled round tabletop (top surface at local y about 2.08, radius 2.5) on a
black stacked column, and five coloured stools around it at radius 3.15 (yellow, blue, teal,
orange, purple). The props on the table are one line (`sheet(meeting,...)`, a black box with a
light screen, a black box with a grey cylinder). When Kapı asks Şef, the agents walk to this
table and sit on the stools, so this is where the story's decisions are talked through.

Replace those props with a table set that reads, from the "table" and "rooms" camera views and
from the floor, as a team briefing about one delivery, in LEGO bricks:

- In front of each of the five stools, a place setting in that stool's colour: a small mug and a
  name card (a folded tent card; no text needed, a coloured stripe is enough).
- In the centre: a model of the delivery, a mini pallet with twelve mini cartons (3 × 4, tan,
  with a tape stripe), clearly the thing being discussed.
- The delivery note on a clipboard, and a tablet on a small stand showing a coloured status
  screen (a green/amber/red three-light bar, nothing legible), facing the hero camera side.
- A conference speakerphone (a flat triangle or round puck with a grey grille), a pen pot, and
  a few loose sheets and sticky notes, slightly rotated, so it looks used.
- Nothing that reads as a single big button or a joystick.

Keep everything inside radius 2.2 of the table centre so the stools' edge stays clear, keep
props low (under about 0.45 above the tabletop) so they never hide the seated agents' faces, and
keep it under about 80 new `box`/`cyl` calls. Use the existing helpers (`box`, `cyl`, `sheet`,
`label`) and colours from `C`; end with `flush(meeting)` as now. No new lights; the tablet
screen may use a soft `toneMapped:false` material.

Change only `site/sim-lego/main.js`, only the meeting-table props line (and small helpers right
above it if needed). Do not move or resize the table, the disk, the stools or anything else; do
not touch routes, collision, UI or the office rooms; do not change `?v=` strings.

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we check it in the browser ourselves.
