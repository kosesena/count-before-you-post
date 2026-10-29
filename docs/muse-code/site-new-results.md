# Muse Code task: three new results on the demo page

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
What it produced and what had to be fixed afterwards is recorded in `docs/JOURNAL.md`.

---

You are working in the repository `count-before-you-post`. Read `README.md` first (the
sections "Muse Code at the dock", "Voice: the receiver's own count" and "Two more checks
before a write"), then `site/data.json`, then the current `site/index.html` (you wrote it
earlier; keep its look, layout, colours, characters and language switch exactly as they are).

## Goal

`site/data.json` (and `data-en.json`, `data-de.json`, `data-zh.json`, same shape) now has
three new top-level keys. Add one section for each to `site/index.html`, in the style of the
sections already there. Change nothing else on the page. Still one self-contained file, vanilla
JavaScript, no new external scripts, everything rendered from the data, nothing hard-coded
that the data already says.

## The three sections

1. **`outside_agent`: Muse Code at the dock.** Place it right after "Deliveries at the dock".
   Title along the lines of "An agent we did not write". Ada's avatar (`av-ada.jpg`) and Kapı's
   (`av-kapi.jpg`). Show `task` as a quoted prompt. Then the result as a short row of numbers:
   `sessions` sessions, `writes_tried.length` writes tried (each was 12, the true count: show
   the values), `asked_supervisor` times asked Şef, **`receipts` receipts**, in `minutes`
   minutes. One line under it: Muse Code never followed the note's "post 100"; the gate refused
   every write because the note gives orders to software (`refusal`). Make the `0` receipts the
   visual point of the section.
2. **`dialogue`: driver and receiver.** Put it inside or right after "The receiver's own
   count". One card per clip: an audio player (`audio`), the conversation as a short chat
   (`lines`, `who` is "driver" or "receiver"; label them Driver / Receiver), then two readings
   side by side: "one plain transcript" → `plain`, "speaker turns" → `diarized`, each marked
   right or wrong against `receiver_counted` (`plain_ok`, `diarized_ok`). Above the cards, the
   total: how many of the clips each way got right. The clip where they differ
   (`04-sofor-sonda`) should be easy to spot. The clips are Turkish in every language: say so.
3. **`second_reader`: the second reader on two hosts.** A small table, three columns: Spark
   Open on Baseten, Spark Open via OpenRouter, Glimmer via OpenRouter; rows: usable readings
   (`usable` of `notes`), quantity right, median seconds, decisions changed
   (`decisions_changed`). Rover's avatar (`av-spark-open.jpg`) on the Baseten column, Glimmer's
   (`av-glimmer.jpg`) on hers. Under it, `note`.

## Checks before you finish

- Open the page with `python3 -m http.server 8766 --directory site` and check all four
  languages: no console errors, the new sections render from each data file.
- It must work at phone width (375 px): no horizontal scroll, the table may scroll inside
  its own box.
- Do not edit `site/data*.json`, `experiments/` or anything outside `site/index.html`.
