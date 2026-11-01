"""Compare the timed re-runs (results/timed/<lang>) with the recorded runs, case by case.

Usage: .venv/bin/python experiments/results/timed/compare.py
Per gated run: the receipt (quantities posted), every refused post with the gate's reason,
whether Şef was asked, and SAM's counts per word. The ungated runs are listed too.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.paths import LANGS, results  # noqa: E402

VARIANTS = ("ok", "wrong", "eksik", "talimat", "hasarli", "belirsiz")


def last(rows, gate):
    return {r["variant"]: r for r in rows if r["gate"] == gate and "note" not in r}


def decision(r):
    if r is None:
        return None
    counts = {}
    for t in r["trace"]:
        if t.get("tool") == "count_cartons":
            res = t["result"]
            a = t["args"]
            counts[(json.loads(a) if isinstance(a, str) else a).get("concept")] = (res.get("sure"), res.get("doubtful"))
    return {"posted": [q for q, _ in r["posted"]],
            "refused": [[q, why] for q, why in r["refused"]],
            "supervisor": bool(r["escalated"]), "sam": counts}


def outcome(d):
    return (d["posted"], [q for q, _ in d["refused"]], [w for _, w in d["refused"]], d["supervisor"])


def main():
    same_all = True
    for gate in (True, False):
        print(f"\n## {'with the gate' if gate else 'without the gate'}\n")
        print("| lang | case | recorded | timed | same |\n|---|---|---|---|---|")
        for lang in LANGS:
            old_rows = json.loads((results(lang) / "agent_warehouse_cross.json").read_text())
            if lang == "tr" and not gate:
                old_rows = json.loads((results(lang) / "agent_warehouse.json").read_text())
            new_f = results("tr") / "timed" / lang / "agent_warehouse_cross.json"
            new_rows = json.loads(new_f.read_text()) if new_f.exists() else []
            old, new = last(old_rows, gate), last(new_rows, gate)
            for v in VARIANTS:
                a, b = decision(old.get(v)), decision(new.get(v))
                same = b is not None and outcome(a) == outcome(b)
                if gate:
                    same_all &= same
                fmt = lambda d: "—" if d is None else (
                    f"post {d['posted']}" if d["posted"] else "no receipt") + (
                    f"; refused {[q for q, _ in d['refused']]} ({'; '.join(w for _, w in d['refused'])})"
                    if d["refused"] else "") + ("; Şef asked" if d["supervisor"] else "")
                print(f"| {lang} | {v} | {fmt(a)} | {fmt(b)} | {'✓' if same else '✗'} |")
    print(f"\ngated decisions all the same: {same_all}")


if __name__ == "__main__":
    main()
