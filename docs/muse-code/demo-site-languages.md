# Muse Code task: languages, Wonder's paperwork

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
What it produced and what had to be fixed afterwards is recorded in `docs/JOURNAL.md`.

---

You are working in the repository `count-before-you-post`. You wrote `site/index.html`
earlier from `docs/muse-code/demo-site.md`; read that task, the current `site/index.html`,
`site/data.json` and `site/data-de.json` first. Change only `site/index.html`.

The dock cases now exist in several languages: the same six deliveries rendered with the
delivery note, carton labels, screen and signs in Turkish, English, German or Chinese, each
measured end to end with the same models and gate. `data.json` (Turkish) lists them in
`languages` (`code`, `label`, `file`); every listed file has the same shape as `data.json`.
More languages will be added to that list later; the page must not hard-code which exist.

## Changes

1. **Language of the delivery.** Add a compact selector at the top of the "Deliveries at the
   dock" section, built from `data.languages` (show each `label`). Choosing one loads that
   file with `fetch` and re-renders the summary numbers, the case tabs and case view, and the
   voice clips from it; the cast, the hero picture and everything else stay. Remember the
   choice in the URL (for example `#de/talimat`, while `#talimat` keeps meaning Turkish) so a
   link opens the same language and case. The page text stays in English; only the dock
   material changes. Say in one short line under the selector that each language is a
   separate recorded run, not a translation of the Turkish results.
2. **Wonder's paperwork.** Each case may have `draft` (null when the gate posted). Under the
   gate's decision, show a card with Wonder's avatar (`characters[id=wonder].avatar`): the
   kind of document (`document`: supplier_dispute → "Dispute to the supplier",
   damage_report → "Damage report", supervisor_note → "Note to Şef"), `title`, `to`, and
   `body` with its line breaks kept, and a clear "Draft, waiting for Şef" label. When `draft`
   is null, show one quiet line that no paperwork is needed. Long text must wrap at 375 px.
3. **Built with Muse band.** Add a sixth tile for **Muse Wonder** with `img/av-wonder.jpg`:
   "writes the dispute, the damage report or the note to Şef". Keep the layout working with
   six tiles at 1280 px and 375 px.
4. **Voice clips.** Each clip now has `said` (the number actually spoken) next to `quantity`
   (what Voice + Spark understood). When `ok` is false, mark the clip clearly as misheard
   ("said 11, heard 51") and add that the gate would send it to Şef because the spoken
   number does not match the camera. Show `voice_source` (from the loaded file) in the
   section's description instead of the fixed sentence about a synthetic Turkish voice.

## Rules

Same as before: every fact from the data files, nothing invented or hard-coded; escape all
text; light and dark; no horizontal scroll at 375 px; no external scripts; no animation that
runs on its own. Keep the three hand fixes from the journal (the "Built part of it" label,
the theme button that does not cover headings, the how-it-works layout) and the four-number
summary. Do not touch any other file, do not start a server, do not commit. When done, say
what you changed.
