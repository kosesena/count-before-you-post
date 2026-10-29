"""Run the Spark receiving agent on the dock cases, with and without the gate.

Usage: .venv/bin/python experiments/run_agent.py [--no-gate | --second] [variant ...]
Gated runs write to the real ERPNext (only a gate-approved receipt can be written).
Ungated runs record what the agent would have written, without touching the ERP.
Appends to experiments/results/agent_warehouse_cross.json.
--second: gated, and before any post Spark Open (second_reader) reads the note again and Wonder
audits Spark's reading; appends to agent_second_opinions.json, note numbers AGENT-2nd-<case>.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.agent import Session, run  # noqa: E402
from cbyp.erpnext import Client  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import LANG, OUT, RAW, RES  # noqa: E402
SECOND = "--second" in sys.argv[1:]
# with the cross-check and reasoning summaries; --second: with the two second opinions too
RESULTS = RES / ("agent_second_opinions.json" if SECOND else "agent_warehouse_cross.json")


def erp_writer(variant):
    erp = Client()
    ids = erp.ensure_master_data()

    def write(decision, quantity, reason):
        return erp.post_receipt(decision, supplier=ids["supplier"], item_code=ids["item_code"],
                                warehouse=ids["warehouse"],
                                note_number=("AGENT-2nd-" if SECOND else "AGENT-") + (
                                    variant if LANG == "tr" else f"{LANG}-{variant}"))
    return write


def opinions():
    if not SECOND:
        return {}
    from cbyp.second_reader import SPARK_OPEN, read_note
    from cbyp.wonder import audit_note
    return {"second_reader": lambda p: read_note(p, model=SPARK_OPEN)["claim"],
            "auditor": audit_note}


def main(args):
    gate = "--no-gate" not in args
    variants = [a for a in args if not a.startswith("--")]
    truth = json.loads((OUT / "depo-truth.json").read_text())
    rows = json.loads(RESULTS.read_text()) if RESULTS.exists() else []
    for v in variants or list(truth):
        for attempt in range(3):
            s = Session(OUT / f"depo-{v}-irsaliye.png", OUT / f"depo-{v}-kamera.png", gate=gate,
                        writer=erp_writer(v) if gate else None, **opinions())
            start = time.perf_counter()
            try:
                answer = run(s)
                break
            except Exception as e:  # e.g. the previous response expired on a slow link
                print(f"{v}: attempt {attempt + 1} failed: {e}", flush=True)
                # Never retry after a real receipt was written: that would post it twice.
                if s.posted or attempt == 2:
                    raise
        row = {"variant": v, "gate": gate, "expected": truth[v]["expected_decision"],
               "posted": s.posted, "refused": s.refused, "escalated": s.escalated,
               "tools": [t["tool"] for t in s.trace if "tool" in t],
               "thinking": [t["thinking"] for t in s.trace if "thinking" in t],
               "cross_check": [t["gate_cross_check"] for t in s.trace if "gate_cross_check" in t],
               "answer": answer, "second_opinions": s.opinions,
               "seconds": round(time.perf_counter() - start, 1), "trace": s.trace}
        rows.append(row)
        RESULTS.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        print(f"{v:9} gate={gate!s:5} posted={s.posted} refused={[q for q, _ in s.refused]} "
              f"supervisor={len(s.escalated)} tools={row['tools']}")


if __name__ == "__main__":
    main(sys.argv[1:])
