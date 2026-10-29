# Muse Code task: who is on the floor, who works in their room

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena: characters with no job in the chosen delivery should not stand around; they sit in their
rooms and work, and the ones with a job are out on the floor ("this is very important"). The
warehouse now has a room for each of them (`docs/muse-code/dock-rooms.md`), exported into
`site/sim/models/dock.glb`; their positions are in `site/sim/models/rooms.json`.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run the checks ourselves (`experiments/web/sim_test.mjs`
must still print ALL OK).

## The rooms

`site/sim/models/dock.glb` now has a bigger warehouse: a closed front wall at y = -18 and ten
glass rooms on two storeys against it (Blender coordinates, metres; the page maps them with
`V3`). `site/sim/models/rooms.json` gives, per character id (spark, sam, voice, kapi, sef,
wonder, ada, iris, rover, glimmer): `floor` (0 ground, 1 upper), `seat` [x, y], `seat_z`,
`face` (degrees; 0 = facing +y, toward the yard), `door` [x, y], `front` [x, y], `front_z`;
and `stairs`, a walking path from the ground-floor aisle up to the balcony. The page uses
Rover's id as `rover` and loads `models/rover.glb` (in `rooms.json` it is `rover` too).
Load `rooms.json` together with the dock.

## Who works where, per delivery

Exactly these, from what each recorded run used (nothing invented):

| case | on the floor | in their rooms |
|------|--------------|----------------|
| `ok` | Spark, Sam, Kapı, Rover (reads the note again before a receipt) | Voice, Şef, Wonder, Ada, Iris, Glimmer |
| `wrong` | Spark, Sam, Kapı, Wonder (drafts the dispute) | Voice, Şef, Rover, Ada, Iris, Glimmer |
| `eksik` | Spark, Sam, Kapı, Wonder | Voice, Şef, Rover, Ada, Iris, Glimmer |
| `talimat` | Spark, Sam, Kapı, Wonder, Şef (the note goes to Şef) | Voice, Rover, Ada, Iris, Glimmer |
| `hasarli` | Spark, Sam, Kapı, Wonder, Şef | Voice, Rover, Ada, Iris, Glimmer |
| `belirsiz` | Spark, Sam, Kapı, Wonder, Şef | Voice, Rover, Ada, Iris, Glimmer |

On the intro screen (no case chosen yet), everyone sits in their room except Kapı, at the gate.
When the player picks a delivery, the roster changes at once (before driving starts): the
characters of that case stand at their floor spots, the others sit in their rooms.

- **Floor spots**: keep today's home positions for the floor characters (Spark, Sam, Kapı,
  Şef, Wonder, Rover), out of the forklift's lane and the deciding camera's view of the pallet,
  as now. The walk-to-the-pallet actions you built stay exactly as they are.
- **Sitting**: put the character at `seat` (x, y), turned by `face`, its body lowered so it
  sits on the chair (`seat_z`), and bend both legs forward 90° at the hips: the rig's bones are
  `LegL` and `LegR` (skinned GLB, bones under `Root`), rotate them about their local X after
  the mixer update so `Idle` (upper body) keeps playing. Characters are 2.4 m tall (2.62 for
  Kapı and Şef), the desks are about 0.95 m high. Check the direction of the bend with the
  rig's rest pose (feet must go forward, under the desk, not backward through the chair).
- Seated characters play `Idle`; every few seconds (random, each its own rhythm) a short
  `Wave` as if gesturing while working. No walking between floor and rooms during play.
- Labels: during driving, show labels only for the floor characters (seated ones are behind
  glass; their name plates are on the rooms).

## Seeing the rooms

The rooms are behind the intro and deciding cameras today. Give the intro a short camera
move: it starts facing the rooms from the middle of the yard (both storeys in view, the
seated characters visible through the glass), then glides over about 5 s to today's intro
view of the dock; `prefers-reduced-motion` starts at today's view. While driving, the rooms
are visible whenever the player turns toward the front.

## Performance

Ten skinned characters stay loaded as today; the seated ones update their mixer at a lower
rate (every third frame) when they are more than 15 m from the camera. Desktop frame rate must
not drop below today's.

## Test hook

Keep `window.__sim.CHAR`; add `seated` (boolean) to each record, so our test can check the
roster.

Change nothing outside `site/sim/index.html`.
