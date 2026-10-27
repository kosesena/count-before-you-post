# Muse Code task: does the demo page match the repository?

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
This is a read-only review; its answer is saved in `site-audit-answer.md` next to this file.

---

You are reviewing the repository `count-before-you-post`. Do not modify, create or delete any
file. Do not start servers, do not commit, do not use the network. Only read files.

The public demo page is `site/index.html`, which renders `site/data.json`; that data is
built by `experiments/build_site.py` from `experiments/results/`. The rest of the repository
(`README.md`, `docs/JOURNAL.md`, `cbyp/`, `tests/`, `experiments/`, `assets/`) records what
the project does and what was measured.

Answer two questions.

1. **Is everything there?** List the results, features and claims the repository documents
   (README, JOURNAL, results files) and say for each one whether the demo page shows it,
   shows part of it, or leaves it out. Examples of what to check: the six dock cases, the
   gate rules, SAM masks and the cross-check, the agent runs with and without the gate, the
   real ERPNext receipts, the voice clips, the delivery-note reading test in several
   languages, the conveyor/video counting with SAM, the cast. For anything left out, say
   whether it belongs on a demo page or is fine to leave in the repository only.

2. **Is it consistent?** Find every place where the page and the repository disagree:
   numbers (counts, thresholds, number of rules, number of tests, seconds), names of models
   and tools, what each character or tool is said to do, the status of planned work
   (Glimmer, Spark Open, real recordings), and any sentence on the page that the
   repository does not support. Check `site/data.json` against the files it was built from,
   and the hard-coded text in `site/index.html` against `cbyp/gate.py` and the README.

For every finding give the file and line (or JSON path) on both sides, what each says, and
how sure you are. Separate real mismatches from wording differences that are still true.
End with a short list of the changes you would make, most important first. Be concrete and
do not invent problems: if something matches, say so.
