"""Send the gate's decisions on the six dock cases to a real ERPNext.

Usage: .venv/bin/python experiments/post_to_erp.py
Reads experiments/results/gate_warehouse.json (from run_gate.py), writes
experiments/results/erp_warehouse.json. Only a "post" decision may create a
Purchase Receipt; everything else must be refused before any request is made.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.erpnext import Client, GateRefused  # noqa: E402
from cbyp.gate import Decision  # noqa: E402

HERE = Path(__file__).parent


def main():
    rows = json.loads((HERE / "results" / "gate_warehouse.json").read_text())
    erp = Client()
    ids = erp.ensure_master_data()
    out = []
    for row in rows:
        d = Decision(row["action"], row["quantity"], row["reasons"], row["evidence"])
        try:
            name = erp.post_receipt(d, supplier=ids["supplier"], item_code=ids["item_code"],
                                    warehouse=ids["warehouse"],
                                    note_number=f"DEMO-{row['variant']}")
            result = {"written": name}
        except GateRefused as e:
            result = {"refused": str(e)}
        out.append({"variant": row["variant"], "action": d.action, **result})
        print(f"{row['variant']:9} {d.action:6} {result}")
    (HERE / "results" / "erp_warehouse.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
