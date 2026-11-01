# Muse Code task: Brick Dock rooms, premium pass (ground floor)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 1 Nov, after round 1 (`sim-lego-rooms-1.md`): "odalarımız premium olsun". What she
flagged while looking at each agent through the crew camera: the reel-to-reel hid Voice's face,
the tripod hid Sam's, the desk lamp crossed Spark's; Spark's lamp looked careless (now a
restaurant-style cordless touch lamp, by hand); the meeting table was too busy; four blue rooms
side by side (Kapı is now cardboard, Voice deep navy). Fixes so far are by hand in the same file.

---

You are working in the repository `count-before-you-post`, on `site/sim-lego/main.js`, the five
ground-floor offices you built in round 1 (inside `if(floor===0){ ... }` in the office loop:
Spark, Şef, Sam, Voice, Kapı). Since then we fixed some things by hand; keep those fixes
(Spark's cordless touch lamp at the desk's left end, Sam's tripod in the back-left corner and
mini pallet beside Sam, Voice's reel-to-reel on a plinth on the floor at the front-left and the
portable speaker on the desk, the flowering pot in each back-right corner, the room colours).

Make these five rooms feel **premium**: a well-designed office you would want to sit in, still
in LEGO bricks and still each agent's own place. Think fewer, better objects:

- Desks: a thicker top with a slightly darker edge band, slim legs or a solid panel; no clutter.
  At most three or four objects on any desk, each at a believable size next to the figure.
- Chairs: a proper office chair (seat, back, a five-star base) in the room's accent colour.
- Floors: a rug under each desk in a colour that suits the room.
- Walls: one framed piece per room (a poster or print in a thin black or wood frame) and a
  shelf with two or three tidy objects; keep the signature pieces (Spark's cork board, Şef's
  shift planner, Sam's carton drawings, Voice's acoustic pads, Kapı's signal panel).
- Light: a soft warm glow under a wall shelf or along the back wall (emissive strip, no new
  lights); the existing `roomLight` stays.
- Remove anything that looks like filler or noise (scattered small boxes, stray sticky notes on
  the floor side, duplicate props).

Hard rules, checked from the crew camera (it looks at each seated figure through the glass
front, from about the desk's front edge):

- **Nothing between the camera and the figure's face**: no object taller than the desk top
  (local y 1.27) within local x -1.05 to -0.25 in front of the figure (z > 0.05).
- Keep the walking lane clear: local x 1.6 to 2.1, z -0.6 to 2.6.
- The figure sits at (-0.65, 0.18, 0.05); keep the chair there.
- Every `box`/`cyl` you add to a child group needs that group flushed (`flush(g)`), or it is
  never drawn: the meeting table lost half its props this way.
- No new lights, no new textures over 256 px, under about 80 `box`/`cyl` calls per room.

Change only `site/sim-lego/main.js`, only inside `if(floor===0){ ... }`. Do not touch the upper
rooms, the balcony, the meeting table, routes, collision, UI, or `?v=` strings.

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we check every room through the crew camera ourselves.
