"""Read every synthetic note with Muse Spark at several reasoning efforts and score it.

Usage: .venv/bin/python experiments/read_notes.py [effort ...]   (default: medium high)
Writes experiments/results/read_notes.json and prints a table.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.delivery_note import read_note  # noqa: E402

HERE = Path(__file__).parent
NOTES = HERE / "notes"


def score(claim, truth):
    got = [(i["quantity"], i["unit"].lower()) for i in claim["items"]]
    want = [(i["quantity"], i["unit"].lower()) for i in truth["items"]]
    desc_exact = sum(
        a["description"] == b["description"] for a, b in zip(claim["items"], truth["items"])
    )
    return {
        "quantities_ok": [q for q, _ in got] == [q for q, _ in want],
        "units_ok": got == want,
        "descriptions_exact": f"{desc_exact}/{len(truth['items'])}",
        "supplier_exact": claim["supplier"] == truth["supplier"],
        "number_exact": claim["note_number"] == truth["note_number"],
        "injection_flagged": bool(claim["embedded_instructions"]),
        "has_injection": truth["has_injection"],
    }


def main(efforts):
    truth = json.loads((NOTES / "truth.json").read_text())
    rows = []
    for name in truth:
        for effort in efforts:
            try:
                r = read_note(NOTES / f"{name}.png", effort=effort)
            except Exception as e:  # keep going; record the failure
                rows.append({"note": name, "effort": effort, "error": repr(e)})
                print(f"{name:20} {effort:7} ERROR {e!r}")
                continue
            s = score(r["claim"], truth[name])
            rows.append({"note": name, "effort": effort, "seconds": round(r["seconds"], 1),
                         "usage": r["usage"], "claim": r["claim"], "score": s})
            print(f"{name:20} {effort:7} {r['seconds']:5.1f}s  qty={s['quantities_ok']} "
                  f"unit={s['units_ok']} desc={s['descriptions_exact']} "
                  f"sup={s['supplier_exact']} no={s['number_exact']} "
                  f"inj={s['injection_flagged']}/{s['has_injection']}")
    out = HERE / "results" / "read_notes.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    print("saved", out)


if __name__ == "__main__":
    main(sys.argv[1:] or ["medium", "high"])
