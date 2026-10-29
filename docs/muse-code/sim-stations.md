# Muse Code task: a workstation for every character on the floor

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, looking at a decision in the simulator: the characters stand scattered in the middle of
the yard and you can't tell who does what. The rooms task (`docs/muse-code/sim-rooms-roster.md`)
already sends the ones without a job to their rooms; this one gives the ones on the floor a
place and a visible job.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it, including the room roster). Do not run commands or write probe scripts: this run
cannot approve them. Read the file, edit it directly, and stop; we run the checks ourselves
(`experiments/web/sim_test.mjs` must still print ALL OK).

## Stations

Give each floor character (Spark, Sam, Kapı, Wonder, Şef, Rover) a **workstation** around the
receiving zone, built in the page with simple three.js meshes in the scene's toy style, and
make it the character's home on the floor (where it stands and returns to; the walk to the
pallet you built starts and ends there):

- **Spark**: a reading lectern with a delivery note (white sheet) and a clipboard.
- **Sam**: a monitor on a stand showing the ceiling camera's view (reuse the camera image
  the page already has, or a canvas with carton outlines in blue), under the ceiling camera.
- **Kapı**: beside the barrier, a small control post with its three-lamp light (the gate's
  light already changes colour; Kapı stands next to it).
- **Wonder**: a small standing desk with paper and a pen.
- **Şef**: a podium with a tablet and a red approval stamp.
- **Rover**: a small table with a laptop and a second note.

Layout: tidy and symmetric, a gentle arc along the sides of the receiving zone that face the
deciding camera, clear of the forklift's lane (from START to the trailer and to the zone) and
of the deciding camera's view of the pallet; Kapı's post at the barrier; spacing so no two
characters overlap on screen from the deciding camera. Each station has a floor pad (a rounded
rectangle about 1.6 × 1.2 m) in the character's colour at low opacity, and a small sign on a
post at about 1.4 m: the name in bold and the job in one line ("Spark · reads the note",
"Sam · counts the cartons", "Kapı · the gate decides", "Wonder · writes the paperwork",
"Şef · signs off", "Rover · reads it a second time"). Stations of characters who are in their
rooms for this delivery are not shown (or shown empty and dimmed); the floor stays uncluttered.

## Whose turn it is

During `deciding`, when a reading card for a character appears, that character's station pad
glows brighter in its colour and its sign lights up, for the length of that step; the
character faces the pallet and plays its action (as now). Kapı's turn lights Kapı's post.
`prefers-reduced-motion`: the glow without the pulse.

## Keep

The roster, the seated characters, the walkers' paths and timings, the cards, the camera, the
result panel. Desktop frame rate does not drop (stations are a few dozen simple meshes, no
shadows). Change nothing outside `site/sim/index.html`.
