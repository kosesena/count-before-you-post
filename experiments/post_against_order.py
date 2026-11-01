"""The three-way match in a real ERPNext: a Purchase Order, and the matching delivery received
against it, only through the gate.

Usage: .venv/bin/python experiments/post_against_order.py
Needs ERPNEXT_* in .env. Reads the gate's recorded decisions (run_gate.py, no API calls) and
writes experiments/results/erp_against_order.json.

1. ensure_order: the Purchase Order for PO-2026-1047, 12 cartons, created once in ERPNext.
2. The matching delivery, received against that order line (the gate said post, 12).
3. A second delivery of 12 on the same, now fully received order: the gate stops it
   (over_order, 0 open) and nothing is sent. ERPNext is not asked to write it.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.erpnext import AlreadyReceived, Client  # noqa: E402
from cbyp.gate import Decision, decide  # noqa: E402
from cbyp.purchase_order import order_for  # noqa: E402

HERE = Path(__file__).parent
RES = HERE / "results"


def main():
    rows = {r["variant"]: r for r in json.loads((RES / "gate_warehouse.json").read_text())}
    readings = {r["variant"]: r for r in json.loads((RES / "check_warehouse.json").read_text())}
    erp = Client()
    ids = erp.ensure_master_data()
    order = order_for("tr")
    ref = erp.ensure_order(order, ids)
    out = {"order": order["number"], **ref}
    print(f"order {order['number']} -> {ref['purchase_order']}")

    ok = rows["ok"]
    d = Decision(ok["action"], ok["quantity"], ok["reasons"], ok["evidence"], ok["rule"])
    try:
        out["received"] = erp.post_receipt(d, supplier=ids["supplier"], item_code=ids["item_code"],
                                           warehouse=ids["warehouse"], note_number="PO-1047-ok",
                                           order_ref=ref)
    except AlreadyReceived as e:
        out["received"] = str(e)
    print("matching delivery:", out["received"])

    # The same order, fully received: the gate stops a second delivery of 12.
    r = readings["ok"]
    again = decide(r["note"], r["sam"]["cardboard box conf"], r["spark"],
                   order=order_for("tr", received=12))
    out["second_delivery_gate"] = {"action": again.action, "rule": again.rule,
                                   "reason": again.reasons[0]}
    print("second delivery, gate:", again.action, again.rule)
    (RES / "erp_against_order.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
