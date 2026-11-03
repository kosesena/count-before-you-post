# Hosted dry-run verification

The existing Vercel project now includes `api/verify.py`. POST requires a demo access code via `X-Verification-Token`; API provider keys are server-side environment variables only. GET exposes configuration availability, never credentials. Use `/verify/`; its local asynchronous service remains supported, with the hosted synchronous endpoint as fallback.

Required production secrets: META_API_KEY, BASETEN_API_KEY, VERIFICATION_ACCESS_CODE. The owner-only local copy of the demo access code is `evaluation/private/hosted-demo-access.txt` (gitignored). Share the demo code only with intended reviewers. It is not a provider API key. Rotate the environment secret after review to revoke access.

Files are processed in an ephemeral temporary directory and deleted on normal success/failure. No report is persisted by this endpoint; the browser can export the result. Provider-side retention is separate. There is no ERP writer. Hosted requests have a 4,000,000-byte encoded JSON cap and a 300-second function limit. Large image/PDF/audio sets use the existing local workflow. Hosted failure retries start a fresh run; they do not reuse the local audio checkpoint. Uploads go to the model providers only after consent and code validation.

This is an access-controlled reviewer demo, not a multi-tenant production service: a shared code has no individual user identity or per-user quota. The code is not embedded in the page, URL, repository, or public test report. Invalid code/origin is rejected before processing; provider error details are suppressed. Four HTTP tests cover unauthorized calls, cross-origin calls, result delivery and error redaction.

References: https://vercel.com/docs/functions/runtimes/python and https://vercel.com/docs/functions/limitations

## Production verification — 3 November 2026

Deployment `4dab8c9` completed successfully. Production GET reported configured; a POST without a code returned 403. An authenticated request with the existing synthetic oil fixture completed in 63.4 seconds: `post`, quantity 12, rule `match`, `erp_written: false`. All 12 objects matched; the second reader and audit completed. Public evidence: `evaluation/hosted-smoke-2026-11-03.json`, also included in `site/validation.json`. This is a connectivity/full-pipeline smoke test, not a new independent accuracy test. The browser showed the hosted access-code form. Four HTTP tests passed.

## Optional counting area

The verification form previews the original photo and accepts a dragged rectangle or exact pixel coordinates. An explicit operator completeness confirmation is required. Both hosted and local servers crop the EXIF-oriented original, use that same crop for all camera models, and attach both original and analyzed image data, hashes, dimensions and coordinates to the downloadable report. Whole-image processing remains the default. Approval of a selected area does not establish delivery completeness or inspect excluded goods. Selection changes invalidate the UI confirmation. The local retry checkpoint retains the immutable cropped file and original provenance. Hosted original-plus-crop report assets over 4 MB are rejected before provider calls; use the local service for larger images.

Three development calls on the same previously inspected SCD 822 image and fixed area returned post/match, block/mismatch and block/wrong_product. The correct case included second reading and audit. Records: `evaluation/counting-area-controls-2026-11-03.json`. Authored notes/orders and synthetic speech; no ERP writes, no independent shipment or field claim.

Production repeat of the selected-area correct control completed in 87.0 seconds on deployment `e119c1b`, returned `post/match`, retained both original and analyzed image evidence, and reported `erp_written: false`. This fourth call is recorded separately from the three development controls. All 140 Python tests passed; the selection form and live review page were checked in the browser.
