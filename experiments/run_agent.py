"""Run the Spark receiving agent on the dock cases, with and without the gate.

Usage: .venv/bin/python experiments/run_agent.py [--no-gate | --second | --dry-run]
       [--out DIR] [variant ...]
Gated runs write to the real ERPNext (only a gate-approved receipt can be written).
Ungated runs record what the agent would have written, without touching the ERP.
--dry-run: gated, but the approved receipt is not written (no document number).
Appends to experiments/results/agent_warehouse_cross.json, or to DIR/ with --out.
--second: gated, and before any post Spark Open (second_reader) reads the note again and Wonder
audits Spark's reading; appends to agent_second_opinions.json, note numbers AGENT-2nd-<case>.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.agent import Session, run
from cbyp.workflow import full_session  # noqa: E402
from cbyp.erpnext import Client  # noqa: E402
from cbyp.purchase_order import order_for  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import LANG, OUT, RAW, RES  # noqa: E402
SECOND = "--second" in sys.argv[1:]
DRY = "--dry-run" in sys.argv[1:]
_out = sys.argv.index("--out") + 1 if "--out" in sys.argv else None
# with the cross-check and reasoning summaries; --second: with the two second opinions too
RESULTS = (Path(sys.argv[_out]) if _out else RES) / (
    "agent_full_checks.json" if "--legacy-core" not in sys.argv and "--no-gate" not in sys.argv else
    "agent_second_opinions.json" if SECOND else "agent_warehouse_cross.json")
RESULTS.parent.mkdir(parents=True, exist_ok=True)


def erp_writer(variant):
    erp = Client()
    ids = erp.ensure_master_data()
    ref = erp.ensure_order(order_for(LANG), ids)

    def write(decision, quantity, reason):
        return erp.post_receipt(decision, supplier=ids["supplier"], item_code=ids["item_code"],
                                warehouse=ids["warehouse"], order_ref=ref,
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
    variants = [a for i, a in enumerate(args) if not a.startswith("--") and i + 1 != _out]
    truth = json.loads((OUT / "depo-truth.json").read_text())
    rows = json.loads(RESULTS.read_text()) if RESULTS.exists() else []
    for v in variants or list(truth):
        for attempt in range(3):
            if gate and "--legacy-core" not in args:
                audio_dir = os.environ.get("CBYP_RECEIVER_AUDIO_DIR")
                if not audio_dir or not (Path(audio_dir) / f"{v}.wav").is_file():
                    raise ValueError("Full checks require CBYP_RECEIVER_AUDIO_DIR/<case>.wav before any model or ERP calls.")
                s = full_session(OUT / f"depo-{v}-irsaliye.png", OUT / f"depo-{v}-kamera.png",
                                 order_for(LANG), writer=erp_writer(v) if not DRY else None,
                                 audio=Path(audio_dir) / f"{v}.wav" if audio_dir else None,
                                 language={"tr":"Turkish","en":"English","de":"German","zh":"Chinese"}[LANG])
            else:
                s = Session(OUT / f"depo-{v}-irsaliye.png", OUT / f"depo-{v}-kamera.png", gate=gate,
                            writer=erp_writer(v) if gate and not DRY else None, order=order_for(LANG),
                            **opinions())
            start = time.perf_counter()
            try:
                answer = run(s)
                break
            except Exception as e:  # e.g. the previous response expired on a slow link
                print(f"{v}: attempt {attempt + 1} failed: {e}", flush=True)
                # Never retry after a real receipt was written: that would post it twice.
                if any(doc for _, doc in s.posted) or attempt == 2:
                    raise
        row = {"variant": v, "gate": gate, "profile": "full" if s.full_checks else "legacy_core", "expected": truth[v]["expected_decision"],
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
