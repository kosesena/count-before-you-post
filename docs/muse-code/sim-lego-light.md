# Muse Code task: Brick Dock lighting

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena asked for it on 1 Nov: Muse Code's earlier lighting work was the best, so the light pass is its job.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator
`site/sim-lego/main.js` (three.js, served at `/sim-lego/`). The geometry, routes and UI are
finished and tested; this round is only about light. Make the warehouse look lit by its lamps,
not by a flat white sky, while keeping the bright, toy-like LEGO palette.

What is there now (top of `main.js`, about lines 24-41): ACES tone mapping at exposure 0.95, a
`RoomEnvironment` at intensity 0.48, a hemisphere light 0.8, one shadow-casting directional "sun"
2.5 from (18,22,8) with a 2048 shadow map, a cool directional fill 0.6. Each office has a warm
point light (`roomLight`, around line 162); the black pendant lamps hanging from the ceiling
give no light at all; the truck has a cargo lamp and the dock a red signal glow.

What we want:

1. **Pendant lamps that light the floor.** Each black ceiling pendant gets a warm emissive
   underside (a small disc that glows, `toneMapped:false` is fine) and a soft warm pool of light
   on the floor below it. Do not add one real light per pendant if that makes the scene heavy:
   a few broad warm SpotLights or PointLights covering the receiving area, the meeting table
   and the rack aisle, plus the emissive discs, is enough. No new shadow-casting lights.
2. **Less flat.** Lower the environment and hemisphere so corners and the space under the
   balcony are a little darker; the main directional light warmer and softer; keep the
   offices' warm glow readable from the floor. The floor must still look light grey, the
   bricks must keep their colours (pink, teal, yellow, orange rooms; blue racks; yellow lines).
3. **Signs and screens.** The hanging green signs and the lit room names already glow; keep
   them readable, do not let them bloom out.

Keep performance: still one shadow map, no post-processing passes, no new textures over 1 MB.
The page must still open on a laptop at a smooth frame rate.

Change only light, emissive and tone-mapping code in `site/sim-lego/main.js`. Do not move or
resize any object, do not touch routes, collision, UI or the other files, and do not change the
`?v=` version strings (we bump them).

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we check it in the browser ourselves.
