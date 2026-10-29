# Muse Code task: rooms as full as the concepts

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After the two furnishing passes, seen in Blender from the yard: the rooms are still big and
nearly empty next to the concepts Sena chose (a desk, a chair, one board in a 6 m room), the
furniture is human-sized while the simulator's characters are 2.4 m tall toys, and the name
plates came out black instead of in the character's colour.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (`p_rooms`, which you wrote and furnished). Do not run
commands or write probe scripts: this run cannot approve them. Read the file, edit it
directly, and stop; we build and look ourselves.

Open the chosen concepts again (`experiments/mockups/room-choices.json` names the variant per
character: `experiments/mockups/room-<id>-<variant>.png`). In them each room is **dense**:
every wall carries something, the desk is crowded, there are things on the floor, the light is
warm. Ours are not. Make every one of the ten rooms read like its concept from the yard:

1. **Scale to the characters.** The simulator's characters are about 2.4 m tall (LEGO
   proportions: hip at about 40 % of the height). Scale every piece of furniture and prop in
   the rooms by 1.25 (desk top at about 0.95 m, seat at about 0.6 m, shelves and boards
   accordingly), and update `seat_z` in `rooms.json`. Storey height stays.
2. **Density.** At least 25 distinct props per room, spread over the whole 6 m: the desk
   crowded with the concept's things; **both side walls** covered over most of their length
   (full-height shelving, boards, pegboards, posters, framed pictures, whatever the concept
   shows); the back wall with its main feature large (Spark's cork board, Sam's carton
   drawings, Kapı's three-lamp panel, Şef's shift planner, Voice's notes, Wonder's pigeonholes
   and map, Ada's whiteboard and "</>" neon, Iris's sketch string, Glimmer's crystal shelves,
   Rover's postcard string); a rug under the desk; a plant or two; a ceiling lamp; things on
   the floor (boxes, cases, a bin). Give props colour, not grey: paper white, wood warm, the
   character's colour as accents, emissive where something glows.
3. **Name plates**: a box 1.8 m × 0.4 m in the character's own colour, the name in bold white,
   both lit (emissive), centred above the room's glass and readable from the middle of the yard.
4. Keep: the seat facing the yard, nothing taller than about 1.15 m between the seat and the
   glass, the doorway clear, the object names `p_room_<id>_*`.

Change nothing outside `experiments/blender/warehouse.py`.
