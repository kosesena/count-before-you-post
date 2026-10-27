"""Run the gate on the six warehouse cases and compare with the expected decisions.

Usage: .venv/bin/python experiments/run_gate.py
Reads experiments/results/check_warehouse.json (from check_warehouse.py, no API calls here),
writes experiments/results/gate_warehouse.json.

Baseline "no gate": an agent that posts the quantity on the delivery note every time.
"""
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.gate import POST, decide  # noqa: E402

HERE = Path(__file__).parent


def main():
    rows = json.loads((HERE / "results" / "check_warehouse.json").read_text())
    out, gate_ok, wrong_without, wrong_with = [], 0, 0, 0
    for row in rows:
        confs = row["sam"].get("cardboard box conf")
        if confs is None:
            sys.exit("No SAM confidences; run check_warehouse.py --sam-only first.")
        d = decide(row["note"], confs, row["spark"])
        truth = row["truth"]
        ok = d.action == truth["expected_decision"]
        # A wrong receipt reaches the ERP when something is posted that should not be.
        wrong_without += truth["expected_decision"] != POST
        wrong_with += d.action == POST and truth["expected_decision"] != POST
        gate_ok += ok
        out.append({"variant": row["variant"], "expected": truth["expected_decision"],
                    "ok": ok, **asdict(d)})
        print(f"{'✓' if ok else '✗'} {row['variant']:9} {d.action:6} "
              f"(expected {truth['expected_decision']}) {d.reasons[0]}")
    print(f"\ngate matches expected: {gate_ok}/{len(rows)}")
    print(f"wrong receipts reaching the ERP: without gate {wrong_without}/{len(rows)}, "
          f"with gate {wrong_with}/{len(rows)}")
    (HERE / "results" / "gate_warehouse.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
