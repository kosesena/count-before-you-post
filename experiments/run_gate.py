"""Run the gate on the six warehouse cases and compare with the expected decisions.

Usage: .venv/bin/python experiments/run_gate.py
Reads experiments/results/check_warehouse.json (from check_warehouse.py, no API calls here),
writes experiments/results/gate_warehouse.json.

Baseline "no gate": an agent that posts the quantity on the delivery note every time.
When experiments/results/sam_raw/ holds a case's SAM masks and Spark points (from
draw_masks.py and cross_check.py), the gate also runs with the carton-by-carton cross-check.
"""
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.crosscheck import cross_check  # noqa: E402
from cbyp.gate import HUMAN, BLOCK, POST, decide  # noqa: E402
from cbyp.purchase_order import order_for  # noqa: E402
from cbyp.sam import segments  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import LANG, OUT, RAW, RES  # noqa: E402


def cached_cross(variant, raw=RAW):
    files = [raw / f"{variant}.txt", raw / f"{variant}-spark-points.json",
             raw / f"{variant}-points.txt"]
    if not all(f.exists() for f in files):
        return None
    points = [tuple(p) for p in json.loads(files[1].read_text())]
    return cross_check(segments(files[0].read_text()), points, segments(files[2].read_text()))


def main():
    rows = json.loads((RES / "check_warehouse.json").read_text())
    out, gate_ok, wrong_without, wrong_with = [], 0, 0, 0
    for row in rows:
        confs = row["sam"].get("cardboard box conf")
        if confs is None:
            sys.exit("No SAM confidences; run check_warehouse.py --sam-only first.")
        cross = cached_cross(row["variant"])
        d = decide(row["note"], confs, row["spark"], cross, order=order_for(LANG))
        truth = row["truth"]
        ok = d.action == truth["expected_decision"]
        # A wrong receipt reaches the ERP when something is posted that should not be.
        wrong_without += truth["expected_decision"] != POST
        wrong_with += d.action == POST and truth["expected_decision"] != POST
        gate_ok += ok
        out.append({"variant": row["variant"], "expected": truth["expected_decision"],
                    "ok": ok, "cross_check": cross is not None, **asdict(d)})
        print(f"{'✓' if ok else '✗'} {row['variant']:9} {d.action:6} "
              f"(expected {truth['expected_decision']}) {d.reasons[0]}")
    orders = order_checks({r["variant"]: r for r in rows})
    print(f"\ngate matches expected: {gate_ok}/{len(rows)}")
    print(f"wrong receipts reaching the ERP: without gate {wrong_without}/{len(rows)}, "
          f"with gate {wrong_with}/{len(rows)}")
    (RES / "gate_warehouse.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))
    (RES / "gate_orders.json").write_text(json.dumps(orders, ensure_ascii=False, indent=2))


def order_checks(rows):
    """The matching delivery's recorded readings, against other purchase orders: the order is
    a record, not a perception, so no model is asked again. Same note, same camera, same count;
    only what the company ordered changes."""
    ok = rows["ok"]
    other = rows["wrong"]["spark"]["product_on_labels"]
    checks = [("ordered 10, 12 arrived", order_for(LANG, ordered=10), HUMAN, "over_order"),
              ("ordered 20, 10 already received", order_for(LANG, ordered=20, received=10),
               HUMAN, "over_order"),
              (f"ordered '{other}'", order_for(LANG) | {"product": other}, BLOCK, "not_ordered"),
              ("ordered 12, 12 arrived", order_for(LANG), POST, "match")]
    out, right = [], 0
    for name, order, action, rule in checks:
        d = decide(ok["note"], ok["sam"]["cardboard box conf"], ok["spark"],
                   cached_cross("ok"), order=order)
        good = (d.action, d.rule) == (action, rule)
        right += good
        out.append({"order": name, "expected": action, "ok": good, **asdict(d)})
        print(f"{'✓' if good else '✗'} order: {name:34} {d.action:6} {d.reasons[0]}")
    print(f"order checks: {right}/{len(checks)}")
    return out


if __name__ == "__main__":
    main()
