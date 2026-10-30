# Muse Code task: the simulator's workstations in the Blender warehouse

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct: the video and the simulator must show the same warehouse. The simulator builds
six floor workstations in three.js (`site/sim/index.html`); the Blender scene, where the
video's stills and shots are rendered, has none.

---

You are working in the repository `count-before-you-post`. Do not run commands or write
probe scripts: this run cannot approve them. Read the files, edit directly, and stop; we
build and render ourselves.

Write a new file `experiments/blender/stations.py` with one function
`build_stations(P, box, cyl, mat)` that builds, in Blender, the six floor workstations the
simulator builds in `site/sim/index.html` (read the `// ---------- floor stations ----------`
section: `STATION_JOB`, `STATION_IDS`, `padGeo`, `signTexture`, `buildSparkFurniture`,
`buildSamFurniture`, `buildKapiFurniture`, `buildWonderFurniture`, `buildSefFurniture`,
`buildRoverFurniture`, `buildStation`, and the `PEOPLE` array for each station's base `b`).
`P` is the dict of polish materials, `box(name, dims, loc, m, rot_z=0.0, bevel=0.0)`,
`cyl(name, r, h, loc, m, rot=(0,0,0), verts=24)` and `mat(name, color, rough=0.7,
metal=0.0, emit=0.0)` are the helpers in `experiments/blender/warehouse.py` (read them; `box`
and `cyl` are centred on `loc`, `dims` are full sizes, Blender is z-up).

**Coordinates.** The simulator maps a scene point with `V3 = (x, y, z) => new
THREE.Vector3(x, z, -y)`: Blender `(x, y, z)` is the simulator's `(x, y)` floor position plus
height z. A station group sits at `V3(b[0], b[1], 0)` with no rotation; inside it three.js
local `(lx, ly, lz)` is Blender `(b[0] + lx, b[1] - lz, ly)`. So the furniture at local
`z = FZ = -0.45` stands at Blender `y = b[1] + 0.45`, toward the receiving zone, and the sign
at local `z = 0.12` is just behind the character. Three.js `BoxGeometry(w, h, d)` is Blender
dims `(w, d, h)`; `CylinderGeometry(r0, r1, h)` stands upright (Blender z). Nested groups
(`top` with `rotation.x`, `lid`, `pagePivot`, `sefHead`) must keep their tilt: build their
children, parent them to an empty at the group's position and rotate the empty by
`(-rotation.x, 0, 0)` about Blender x (three's +x rotation tips the +y axis toward +z, which
is Blender's tip from +z toward -y; check the sign on Spark's lectern so its top tilts toward
the reader, i.e. the high edge away from the character).

Build per station, with the same sizes and colours (hex colours from the JS → linear RGB via
the sRGB transfer function; `roughness`/`metalness` as given):

- the rounded pad (1.6 × 1.2 m, corner radius 0.28) as a thin flat mesh 1 cm above the floor
  in the character's colour (`CHAR_COL_FALLBACK`), at 35 % alpha via a Principled BSDF alpha
  (blend mode for EEVEE, alpha works in Cycles);
- the sign post and the 0.8 × 0.35 × 0.04 board at the same place, its printed face on
  Blender −y (in the JS the face is material index 4, three's +z face, i.e. Blender −y: away
  from the zone, toward the cameras south of the stations): put a text object on that face: the character's name in bold white (size ~0.11)
  and the job line from `STATION_JOB` below it in the character's colour (size ~0.06), on a
  dark navy board with a border in the character's colour (a slightly larger box behind it);
- all the furniture of `buildSparkFurniture` … `buildRoverFurniture`, every mesh, with the
  three.js canvas screens replaced by emissive planes in the screen's main colour (Sam's
  monitor dark navy `#0a1424` with emission 1.5 and a few cyan box outlines as thin emissive
  strips, Şef's tablet `#e8eef7` with a green tick of two thin bars, Rover's laptop dark with
  a teal header strip, Kapı's three lamps emissive red/amber/green with the **green lit**
  (emission 6) and red/amber dim (0.3), because this file is the `ok` case);
- skip the dynamic pieces that only exist for animation (Spark's turning page may be one
  static sheet lying on the lectern; Şef's red stamp mark stays hidden; Wonder's stack empty).

Name every object `p_station_<id>_*` and put them in a collection `stations`. Take the six
`b` values from `PEOPLE` in `site/sim/index.html` as constants at the top of the file with a
comment saying where they come from (spark, sam, kapi, wonder, sef, rover). Add an argument
`ids=("spark", "sam", "kapi", "wonder", "sef", "rover")` so a caller can build only the floor
set of one case.

Change nothing else in the repository.
