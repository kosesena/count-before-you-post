# Local character repairs

These are derived copies of the project's existing Meshy GLBs; shared `/sim/models/` files were not replaced.

- `rover-clean.glb`: removed the single disconnected floor-prop component (8,352 welded vertices / 9,279 source vertices), preserving material, rig and Idle/Walk/Wave clips.
- `sef-refined.glb`: retained original body, limbs and textures; rebuilt the head, printed-face geometry and hardhat as clean rigid parts bound to Body. Reduced the existing Wave shoulder rotation to 50 degrees with a small sway. Idle and Walk retained. The warehouse uses subtle speech gestures, not the full wave clip.
- `rover-avatar.png`: existing project portrait copied from `assets/mascots/hero/rover.png`.

Prepared locally in Blender; no paid generation used. Source assets remain available for comparison or rollback. These changes do not alter the main site's cast media.
