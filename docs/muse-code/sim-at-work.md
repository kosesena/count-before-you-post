# Muse Code task: characters at work, watching, reacting

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, after the layout round: the characters still look like they are just standing there.
The GLBs only have `Idle`, `Walk` and `Wave`, but the rig has separate bones (`Root`, `Body`,
`ArmL`, `ArmR`, `HairSway`, `LegL`, `LegR`), so each character's job can be animated in code.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run the checks ourselves (`experiments/web/sim_test.mjs`
must still print ALL OK, and we measure from the deciding camera that nobody covers the pallet,
the gate's screen or each other, so **don't move anyone's home, station or walk spot**).

## 1. Each floor character works at its station (procedural, on top of `Idle`)

Apply small rotations to the arm bones (and `Body` for a slight lean) after the mixer update,
blended in and out over about 0.3 s, each character on its own rhythm (random phase), smooth
easing, no snapping. Only while the character stands at its station and is not walking or
playing `Wave`. Find the bones by name in each skinned model (`ArmL`, `ArmR`, `Body`); check the
rotation axis against the rest pose so arms move forward/up, not into the body.

- **Spark**: reads at the lectern: right arm lifts and turns a page every 3–4 s (a sheet mesh on
  the lectern turns over with it), slight forward lean while reading.
- **Sam**: holds the tablet up toward the pallet (both arms raised forward, held), and a soft
  blue scanning beam (a thin translucent plane or cone from the ceiling camera) sweeps slowly
  over the pallet while Sam is on the floor.
- **Wonder**: writes at the desk: right hand makes small quick movements; every few seconds a
  new sheet is added to a small stack on the desk (up to 8, then it resets on a new delivery).
- **Şef**: stamps: arm rises, comes down with a quick "tak" (the stamp mesh moves with it), and a
  small red stamp mark appears on the paper on the podium; every 4–5 s.
- **Rover**: types on the laptop: both forearms small alternating movements; now and then turns
  the body slightly toward its note and back.
- **Kapı**: holds the barrier pole and checks it (small tilt of the arm), the lamps on its post
  blink in turn (red, amber, green) until the decision, then show the decision's colour.

## 2. Attention

- While driving, a floor character turns (the whole figure, smoothly, at most about 60° from
  its station heading) to follow the forklift while it is within about 6 m, then turns back.
- When the pallet is set down in the zone, everyone on the floor turns to face the pallet.
- During `deciding`, while a reading card belongs to a character, the others on the floor turn
  to look at that character; Kapı's card: everyone looks at Kapı.

## 3. Reacting to the decision (when Kapı's card shows)

- **POST**: everyone on the floor waves (`Wave`), Kapı's barrier opens as now.
- **BLOCK**: everyone on the floor shakes the body gently left-right twice (`Body` rotation, a
  "no"), arms crossing in front (both arm bones inward), then back to work.
- **ASK ŞEF**: everyone turns to Şef (if Şef is on the floor), Şef steps forward about 0.5 m and
  waves; if Şef is in the room, everyone turns toward Şef's room.

Seated characters in their rooms keep working as now (no change). `prefers-reduced-motion`:
no procedural arm loops or shakes; only the turning to face (instant) and the existing waves.
Desktop frame rate must not drop (a few bone rotations per character per frame).

Change nothing outside `site/sim/index.html`.
