#!/bin/sh
# The whole dock pipeline for one language, in order. Usage: experiments/run_language.sh en|de|zh
# Run one language at a time: three at once time out on a slow uplink. Reading resumes.
# Render first: CBYP_LANG=<lang> Blender -b --factory-startup -P experiments/blender/warehouse.py -- experiments/blender/out/<lang>
set -e
export CBYP_LANG="$1"
PY=".venv/bin/python -u"
$PY experiments/check_warehouse.py      # Spark reads the note and looks; SAM counts
$PY experiments/draw_masks.py           # SAM masks, cached in results/<lang>/sam_raw
$PY experiments/cross_check.py          # carton by carton
$PY experiments/run_gate.py             # the gate, no API calls
$PY experiments/run_agent.py --no-gate  # the agent on its own (no ERP writes)
$PY experiments/run_agent.py            # the agent behind the gate (real ERPNext)
