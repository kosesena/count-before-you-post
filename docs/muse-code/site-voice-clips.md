# Muse Code task: the receiver's voice clips, as one compact glass tile

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena asked for chapter 03's clips to look like the "Receiver's voice clips" tile in
`experiments/mockups/hero-rest-bento.png`.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote it).
Change only chapter 03 ("The receiver"), plus a favicon.

1. Look at the "Receiver's voice clips" tile in `experiments/mockups/hero-rest-bento.png`.
   Rebuild chapter 03 in that spirit: one frosted-glass tile holding the four receiver clips
   (`renderVoice`) as compact rows, each row a round play button, a small waveform drawn from
   the audio (decode it with Web Audio on first play or when visible; until then a neutral
   placeholder bar), the transcript in quotes, what was heard (number, sure / not sure), and the
   duration. A second tile in the same style for the driver-and-receiver dialogues
   (`renderDialogue`): each row the clip's two speaker lines, its play button and waveform, and
   the two readings side by side (one plain transcript vs speaker turns, right / wrong), the
   `04-sofor-sonda` row highlighted. Keep the totals line (4 of 5 vs 5 of 5). One clip plays at
   a time; the playing row shows progress over its waveform.
2. Add a favicon: an inline SVG data URI in `<head>` (a small orange rounded square with a
   white check mark), so the page stops asking for `/favicon.ico`.

Keep every id (`#voice`, `#dialogue`, `#voiceSub`, `#dialogueSub`) and every fact as it is.
Light and dark theme, 375 px without sideways scroll, no console errors. Change nothing
outside `site/index.html`.
