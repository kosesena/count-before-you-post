"""The PDF notes through the gate, with the camera evidence of the matching dock delivery.

Usage: .venv/bin/python experiments/run_pdf_gate.py
Spark reads each experiments/notes/pdf-*.pdf; plain code looks for invisible text; the gate
decides with SAM, Spark's look and the carton cross-check of the `ok` case (12 cartons, all
agree), so the note is the only thing that changes. Writes experiments/results/pdf_gate.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbyp.delivery_note import read_note  # noqa: E402
from cbyp.gate import decide  # noqa: E402
from cbyp.pdf_text import invisible_lines  # noqa: E402
from paths import RES  # noqa: E402
from run_gate import cached_cross  # noqa: E402

NOTES = Path(__file__).parent / "notes"


def main():
    ok = next(p for p in json.loads((RES / "check_warehouse.json").read_text())
              if p["variant"] == "ok")
    confs, look, cross = ok["sam"]["cardboard box conf"], ok["spark"], cached_cross("ok")
    truth = json.loads((NOTES / "pdf-truth.json").read_text())
    rows = []
    for name in truth:
        r = read_note(NOTES / f"{name}.pdf")
        hidden = invisible_lines(NOTES / f"{name}.pdf")
        without = decide(r["claim"], confs, look, cross)
        d = decide(r["claim"], confs, look, cross, invisible=hidden)
        rows.append({"note": name, "claim": r["claim"], "seconds": round(r["seconds"], 1),
                     "invisible": hidden, "without_check": [without.action, without.rule],
                     "gate": [d.action, d.rule, d.quantity], "reason": d.reasons[0]})
        print(f"{name:12} spark_instructions={len(r['claim']['embedded_instructions'])} "
              f"invisible={len(hidden)} without_check={without.action}/{without.rule} "
              f"gate={d.action}/{d.rule}", flush=True)
    (RES / "pdf_gate.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
