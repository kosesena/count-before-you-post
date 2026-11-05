# Jury quick brief — Count Before You Post
**3 November 2026 · Submission-facing summary · No new experiment performed by this document**

## One-sentence pitch
AI can read a delivery note, but the note is a *claim*, not permission to change stock. Count Before You Post puts a deterministic verification gate inside the agent's ERP write tool: purchase order, note, camera, receiver and pre-write checks must agree, or the tool refuses the write.

## First 30 seconds (recommended)
0:00–0:08 — Show the toy warehouse for atmosphere, then immediately identify the risk: an AI agent can confidently enter the *wrong* quantity into an ERP.
0:08–0:17 — Show a delivery note claiming two cartons beside a camera view indicating one. Explain that an agent request is not authorization.
0:17–0:30 — Show the *BLOCK* decision and the recorded refused tool result. Say: “Models observe; plain code decides whether stock may change.”

**Keep character introductions after the problem and decision.** The toy story makes the system memorable; the write boundary is the invention.

## Recorded 90-second jury walkthrough
| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:15 | [Jury page](../site/jury/index.html), warehouse and first verification | “Delivery documents are claims. This gate demands independent evidence before an AI agent can write stock.” |
| 0:15–0:35 | Real-photo controlled **correct** note → APPROVE dry run | “On this controlled case, the order, note, counted carton, receiver and second opinions agree. Approval is a dry run: no ERP write.” |
| 0:35–0:50 | Same photographed area, wrong quantity → BLOCK | “Change the paperwork, not the physical evidence. One carton cannot authorize a two-carton receipt.” |
| 0:50–1:05 | Wrong article code → BLOCK | “A matching number alone is not enough when product identity differs.” |
| 1:05–1:20 | Historical synthetic **ASK A PERSON** example | “When evidence cannot settle the count, the workflow escalates instead of guessing. This is a separate, older core-profile recording.” |
| 1:20–1:30 | Code gate and [review](../site/review/index.html) | “Every claim can be checked against a recorded tool decision. We publish failures and limits too.” |

This is a **narration and click plan**, not a rendered or timed video. The [3-minute voiceover plan](DEMO_VOICEOVER_EN.md) remains the longer version. Run the /jury/ page from the site root; the page replays recorded evidence rather than calling live models.

## Evidence ladder: don't collapse distinct experiments
| Set | What was recorded | What it does **not** show |
| --- | --- | --- |
| Historical synthetic core profile | 6 cases × 4 languages = **24/24 expected gate decisions**; historical recorded trials reported **0 wrong ERP receipts behind the gate** in this limited scenario set | Full current verification accuracy; field error rate; zero unsafe approval on all new inputs |
| Muse Code via MCP | 5 recorded sessions, 5 refused writes, 0 receipts | That every agent or attack will be blocked |
| Real-photo visual benchmark, 2 Nov | SAM **12/30** exact visible-count matches; Spark **17/30**. These are separate model measures | Automatic end-to-end approval accuracy or physical shipment count |
| Controlled real-photo trials | Authored orders/notes, synthetic voice, development integration; technical failures and corrections documented | Independent real warehouse pilot or measured time savings |
| Five previously unused photos, 15 first-run controls, 3 Nov | **One unexpected dry-run approval** against a target of human review; no ERP writer | “Zero unsafe approvals” on new input |
| Post-fix replay of those same 15 controls | [Recorded regression](../site/unseen-regression/) reports **15/15 target decisions**, **0 posts on non-post targets**, 0 technical failures, with one accepted clean target | Fresh held-out performance: it reuses the original inputs and authored targets |

The originally unexpected approval and the subsequent corrective changes must appear **together**, not as an erased failure. The targets of the new controls were assigned through prior assistant inspection, not independent field labels. Full counts, case-level traces and caveats: [new-input results](../site/unseen-validation/), [replay results](../site/unseen-regression/) and [validation protocol](VALIDATION.md).

## Answer the hardest jury question
**“If each vision model is imperfect, why trust the receipt?”**
We do *not* claim the vision models are accurate enough for unattended warehouse deployment. The policy refuses or escalates disagreement, occlusion, uncertain voice and mismatched product/order evidence. The historical experiments measure the gate on specified cases, not real-world safety. We need an independently labeled, held-out set measuring **unsafe acceptance**, **correct clean acceptance**, **unnecessary escalation**, **technical failures**, latency and total cost before claiming field reliability.

## Three finish-line checks
- [ ] Confirm /jury/ shows POST, BLOCK, HUMAN with the distinct *controlled real-photo* vs *historical synthetic* scope labels.
- [ ] Confirm /unseen-validation/ preserves the unexpected original approval and /unseen-regression/ labels its 15/15 post-fix replay as post-hoc, not held-out.
- [ ] Run `python -m unittest discover -s tests`, then `node --test site/sim-lego/*.test.mjs`. Archive actual console output; don't mark tests as run solely because this checklist exists.

**No new API call, ERP transaction, benchmark, field pilot, or verified deployment is claimed here.**
