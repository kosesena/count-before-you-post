# Muse Code task: Brick Dock lighting, round 2

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
What we saw after round 1 (`docs/muse-code/sim-lego-light.md`), measured in the browser pane
on the "rooms" view, same machine, old light vs round 1: 14.7 fps → 10.7 fps, and the scene
looked almost the same (slightly warmer, no visible pools under the pendants).

---

You are working in the repository `count-before-you-post`, on `site/sim-lego/main.js` (you did
the first light pass). Round 1 cost about a quarter of the frame rate and the difference is hard
to see. This round must look clearly better and cost nothing measurable.

1. **Remove the three SpotLights** you added under the pendants (the `for` loop after the
   `fill` light). Every real light adds work to every brick's material, which is where the frame
   rate went.
2. **Fake the light pools instead.** Under each ceiling pendant (the `for(let x=-7;x<=11;x+=9)
   for(let z=-16;z<=14;z+=6)` loop), put a soft warm pool on the floor: one flat plane just
   above the floor (y about 0.21, skip any pendant whose spot is covered by a rack, an office or
   the table platform if that is easy), with one shared radial-gradient CanvasTexture (warm
   centre fading to fully transparent), additive blending, `depthWrite:false`,
   `toneMapped:false`, diameter about 6-7 m, strength so it reads clearly as a lamp pool on the
   light grey studs but never turns the floor white. One shared material and geometry for all
   pools.
3. **Make the lamps themselves read as lit.** The underside discs (`pendantGlow`) should look
   clearly on from the default and "rooms" views: brighter warm emissive, plus a small soft
   additive halo sprite just under each disc (there is already `haloMat` / `halo()` in the file;
   reuse it).
4. **Keep the rest of round 1** (lower environment and hemisphere, warmer softer sun) only if the
   scene still looks bright and the brick colours stay true; if the scene got dull, raise the
   ambient back a little. No new lights of any kind, one shadow map, no post-processing.

Change only `site/sim-lego/main.js`, only light, emissive, halo and floor-pool code. Do not move
or resize other objects, do not touch routes, collision or UI, do not change `?v=` strings.

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we measure the frame rate and look at it in the browser ourselves.
