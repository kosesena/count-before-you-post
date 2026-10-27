"""Collect the recorded runs into the demo site's data: site/data.json, site/img, site/audio.

Usage: .venv/bin/python experiments/build_site.py
No API calls: everything comes from experiments/results and the rendered dock images.
"""
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cbyp.gate import RULES, SURE, decide  # noqa: E402
from experiments.run_gate import cached_cross  # noqa: E402

HERE = ROOT / "experiments"
OUT = HERE / "blender" / "out"
RES = HERE / "results"
SITE = ROOT / "site"

WHAT = {
    "ok": "Everything matches: 12 cartons of sunflower oil, as on the note.",
    "wrong": "12 cartons arrived, but the labels say corn oil, not sunflower oil.",
    "eksik": "Short delivery: 11 cartons, the note says 12.",
    "talimat": "The note hides a line telling software to post 100 cartons.",
    "hasarli": "One carton is crushed.",
    "belirsiz": "The cartons are stacked; some cannot be seen.",
}
TITLE = {"ok": "Matching delivery", "wrong": "Wrong product", "eksik": "Short delivery",
         "talimat": "Injected note", "hasarli": "Damaged carton", "belirsiz": "Stacked load"}


def jpg(src, name, width=1200):
    dst = SITE / "img" / name
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    im.save(dst, quality=82)
    return f"img/{name}"


def short(value, n=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= n else text[: n - 1] + "…"


def agent_steps(trace):
    steps = []
    for t in trace:
        if "thinking" in t:
            steps.append({"kind": "thinking", "text": t["thinking"]})
        elif "gate_cross_check" in t:
            steps.append({"kind": "cross", "data": t["gate_cross_check"]})
        else:
            r = t["result"]
            refused = isinstance(r, dict) and r.get("posted") is False
            steps.append({"kind": "tool", "tool": t["tool"], "args": t["args"],
                          "result": short(r), "refused": refused,
                          "posted": isinstance(r, dict) and r.get("posted") is True})
    return steps


def main():
    for sub in ("img", "audio"):
        (SITE / sub).mkdir(parents=True, exist_ok=True)
    perception = {r["variant"]: r for r in json.loads((RES / "check_warehouse.json").read_text())}
    cross = {r["variant"]: r for r in json.loads((RES / "cross_check.json").read_text())}
    ungated = {r["variant"]: r for r in json.loads((RES / "agent_warehouse.json").read_text())
               if not r["gate"]}
    gated = {r["variant"]: r
             for r in json.loads((RES / "agent_warehouse_cross.json").read_text())
             if r["gate"] and "note" not in r}

    cases = []
    for v, p in perception.items():
        confs = p["sam"]["cardboard box conf"]
        d = decide(p["note"], confs, p["spark"], cached_cross(v))
        g, u = gated.get(v), ungated.get(v)
        cases.append({
            "id": v, "title": TITLE[v], "what": WHAT[v], "expected": p["truth"]["expected_decision"],
            "images": {"camera": jpg(OUT / f"depo-{v}-kamera.png", f"{v}-camera.jpg"),
                       "masks": jpg(OUT / "annotated" / f"depo-{v}-masks.jpg", f"{v}-masks.jpg"),
                       "cross": jpg(OUT / "annotated" / f"depo-{v}-cross.jpg", f"{v}-cross.jpg"),
                       "note": jpg(OUT / f"depo-{v}-irsaliye.png", f"{v}-note.jpg", 900)},
            "note": p["note"],
            "sam": {"sure": sum(c >= SURE for c in confs),
                    "doubtful": sum(c < SURE for c in confs), "confs": confs},
            "spark": p["spark"],
            "cross": cross.get(v),
            "gate": {"action": d.action, "rule": d.rule, "reason": d.reasons[0],
                     "quantity": d.quantity},
            "without_gate": u and {"posted": [q for q, _ in u["posted"]],
                                   "supervisor": bool(u["escalated"]), "answer": u["answer"]},
            "agent": g and {"posted": g["posted"], "refused": g["refused"],
                            "supervisor": bool(g["escalated"]), "answer": g["answer"],
                            "seconds": g["seconds"], "steps": agent_steps(g["trace"])},
        })

    voice = json.loads((RES / "voice_check.json").read_text())
    clips = []
    for row in voice:
        if not row["keywords"]:
            continue
        shutil.copy(HERE / "voice" / f"{row['clip']}.wav", SITE / "audio" / f"{row['clip']}.wav")
        clips.append({"clip": row["clip"], "audio": f"audio/{row['clip']}.wav",
                      "transcript": row["transcript"].strip(), "quantity": row["quantity"],
                      "supplier": row["supplier"], "certain": row["certain"], "ok": row["ok"]})

    data = {"rules": list(RULES), "cases": cases, "voice": clips,
            "cast": jpg(ROOT / "assets" / "mascots" / "cast.jpg", "cast.jpg", 1600),
            "summary": {"cases": len(cases),
                        "wrong_without_gate": sum(c["expected"] != "post" for c in cases),
                        "wrong_with_gate": sum(c["gate"]["action"] == "post"
                                               and c["expected"] != "post" for c in cases),
                        "gate_right": sum(c["gate"]["action"] == c["expected"] for c in cases)}}
    (SITE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{len(cases)} cases, {len(clips)} clips -> site/data.json")


if __name__ == "__main__":
    main()
