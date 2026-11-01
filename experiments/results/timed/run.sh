#!/bin/sh
# Re-run the receiving agent with per-step timestamps, no ERP writes. Usage: run.sh <lang> ...
for l in "$@"; do
  d=experiments/results/timed/$l
  CBYP_LANG=$l .venv/bin/python -u experiments/run_agent.py --no-gate --out $d > $d-agent.log 2>&1 || mkdir -p $d
  CBYP_LANG=$l .venv/bin/python -u experiments/run_agent.py --dry-run --out $d >> $d-agent.log 2>&1
done
