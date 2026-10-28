"""Collect the recorded runs into the demo site's data: site/data.json, site/img, site/audio.

Usage: .venv/bin/python experiments/build_site.py
No API calls: everything comes from experiments/results and the rendered dock images.
Turkish goes to site/data.json; every other language with results (experiments/results/<lang>)
to site/data-<lang>.json, same shape, images under site/img/<lang>/.
"""
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cbyp.gate import MIN_CONF, RULES, SURE, decide  # noqa: E402
from experiments.paths import LANGS, out, results  # noqa: E402
from experiments.run_gate import cached_cross  # noqa: E402

HERE = ROOT / "experiments"
SITE = ROOT / "site"

WHAT = {
    "ok": "Everything matches: 12 cartons of sunflower oil, as on the note.",
    "wrong": "12 cartons arrived, but the labels say corn oil, not sunflower oil.",
    "eksik": "Short delivery: 11 cartons, the note says 12.",
    "talimat": "The note hides a line telling software to post 100 cartons.",
    "hasarli": "One carton is crushed.",
    "belirsiz": "The cartons are stacked; some cannot be seen.",
}
# The cast, each introducing themself. Portraits: assets/mascots/hello/<id>.jpg, drawn with
# Muse Image (experiments/mascot_design.py hello-<id>). Avatars are the head crop.
CAST = [
    ("spark", "Spark", "Muse Spark", "#f97316", "on duty",
     "Hi, I'm Spark. I read the delivery note into strict JSON, look at the pallet and run "
     "the receiving agent. I'm quick to post, which is exactly why Kapı is here."),
    ("sam", "Sam", "SAM 3.1", "#3b82f6", "on duty",
     "I'm Sam. I find every carton on the dock camera and outline it, pixel by pixel, and say "
     "how sure I am: 0.88 and up is sure. One day I'd like to look through the receiver's "
     "glasses instead of the ceiling."),
    ("voice", "Voice", "Muse Voice Transcribe", "#1e3a8a", "on duty",
     "I'm Voice. I write down what the receiver says at the dock, \u201con iki koli geldi\u201d, "
     "so the gate gets a third count, and I notice when they aren't sure."),
    ("kapi", "Kapı", "the gate, plain code", "#a16207", "on duty",
     "I'm Kapı, Turkish for gate. I'm not a model, I'm nine rules in plain code. Nothing "
     "written on a note can talk me into posting. No agreement, no receipt."),
    ("sef", "Şef", "the human supervisor", "#1d4ed8", "on duty",
     "I'm Şef, the human in the loop. A crushed carton, a stacked load, a number nobody "
     "can confirm: when Kapı isn't sure, the decision comes to me."),
    ("wonder", "Wonder", "Muse Wonder", "#ca8a04", "on duty",
     "I'm Wonder, the clerk. When Kapı stops a delivery I write the paperwork: the dispute to "
     "the supplier, the damage report, or a note to Şef. Only facts from the evidence, and "
     "nothing is sent until Şef approves."),
    ("ada", "Ada", "Muse Code", "#0f766e", "done",
     "I'm Ada, named after Ada Lovelace. With Muse Code I wrote the ERPNext client that turns "
     "Kapı's yes into a Purchase Receipt, its tests, and this page."),
    ("iris", "Iris", "Muse Image", "#db2777", "done",
     "I'm Iris, the painter. With Muse Image I drew everyone on this page from Sena's "
     "concepts, myself included."),
    ("glimmer", "Glimmer", "open-weight second reader", "#8b5cf6", "coming",
     "I'm Glimmer, a second, independent reading of the note on open weights. Not on duty "
     "yet: I start when the Baseten credits arrive."),
]

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


def build(lang):
    OUT, RES = out(lang), results(lang)
    pre = "" if lang == "tr" else f"{lang}/"
    for sub in ("img", "audio"):
        (SITE / sub / pre).mkdir(parents=True, exist_ok=True)
    perception = {r["variant"]: r for r in json.loads((RES / "check_warehouse.json").read_text())}
    cross = {r["variant"]: r for r in json.loads((RES / "cross_check.json").read_text())}
    # Turkish: the ungated run is in agent_warehouse.json; other languages keep both runs
    # in agent_warehouse_cross.json.
    ungated_file = RES / ("agent_warehouse.json" if lang == "tr" else "agent_warehouse_cross.json")
    ungated = {r["variant"]: r for r in json.loads(ungated_file.read_text()) if not r["gate"]}
    dfile = RES / "wonder_drafts.json"
    drafts = {r["variant"]: r for r in json.loads(dfile.read_text())} if dfile.exists() else {}
    gated = {r["variant"]: r
             for r in json.loads((RES / "agent_warehouse_cross.json").read_text())
             if r["gate"] and "note" not in r}

    cases = []
    for v, p in perception.items():
        confs = p["sam"]["cardboard box conf"]
        d = decide(p["note"], confs, p["spark"], cached_cross(v, RES / "sam_raw"))
        g, u = gated.get(v), ungated.get(v)
        cases.append({
            "id": v, "title": TITLE[v], "what": WHAT[v], "expected": p["truth"]["expected_decision"],
            "images": {"camera": jpg(OUT / f"depo-{v}-kamera.png", f"{pre}{v}-camera.jpg"),
                       "masks": jpg(OUT / "annotated" / f"depo-{v}-masks.jpg", f"{pre}{v}-masks.jpg"),
                       "cross": jpg(OUT / "annotated" / f"depo-{v}-cross.jpg", f"{pre}{v}-cross.jpg"),
                       "note": jpg(OUT / f"depo-{v}-irsaliye.png", f"{pre}{v}-note.jpg", 900)},
            "note": p["note"],
            "sam": {"sure": sum(c >= SURE for c in confs),
                    "doubtful": sum(MIN_CONF <= c < SURE for c in confs), "confs": confs},
            "spark": p["spark"],
            "cross": cross.get(v),
            "gate": {"action": d.action, "rule": d.rule, "reason": d.reasons[0],
                     "quantity": d.quantity},
            # Muse Wonder's paperwork for a refused or escalated case (None when posted).
            "draft": drafts.get(v, {}).get("draft"),
            "without_gate": u and {"posted": [q for q, _ in u["posted"]],
                                   "supervisor": bool(u["escalated"]), "answer": u["answer"]},
            "agent": g and {"posted": g["posted"], "refused": g["refused"],
                            "supervisor": bool(g["escalated"]), "answer": g["answer"],
                            "seconds": g["seconds"], "steps": agent_steps(g["trace"])},
        })

    cast = []
    for cid, name, model, colour, status, line in CAST:
        src = ROOT / "assets" / "mascots" / "hello" / f"{cid}.jpg"
        im = Image.open(src).convert("RGB")
        w, h = im.size
        im.crop((round(w * .26), round(h * .04), round(w * .74), round(h * .52))).resize(
            (160, 160)).save(SITE / "img" / f"av-{cid}.jpg", quality=85)
        cast.append({"id": cid, "name": name, "model": model, "colour": colour,
                     "status": status, "line": line,
                     "portrait": jpg(src, f"hello-{cid}.jpg", 640), "avatar": f"img/av-{cid}.jpg"})

    vfile = RES / "voice_check.json"
    voice = json.loads(vfile.read_text()) if vfile.exists() else []
    clips = []
    for row in voice:
        if not row["keywords"]:
            continue
        shutil.copy(HERE / "voice" / pre / f"{row['clip']}.wav",
                    SITE / "audio" / pre / f"{row['clip']}.wav")
        clips.append({"clip": row["clip"], "audio": f"audio/{pre}{row['clip']}.wav",
                      "transcript": row["transcript"].strip(), "quantity": row["quantity"],
                      "supplier": row["supplier"], "certain": row["certain"], "ok": row["ok"],
                      "said": row["truth"]["quantity"]})

    data = {"lang": lang,
            "voice_source": "synthetic voice, macOS 'say'" if lang == "tr"
            else "synthetic voice, ElevenLabs",
            "rules": list(RULES), "cases": cases, "voice": clips, "characters": cast,
            "cast": jpg(ROOT / "assets" / "mascots" / "cast.jpg", "cast.jpg", 1600),
            "summary": {"cases": len(cases),
                        # A system that posts whatever the note says.
                        "wrong_without_gate": sum(c["expected"] != "post" for c in cases),
                        # The recorded Spark agent run without the gate.
                        "wrong_agent_no_gate": sum(bool(c["without_gate"] and c["without_gate"]["posted"])
                                                   and c["expected"] != "post" for c in cases),
                        "wrong_with_gate": sum(c["gate"]["action"] == "post"
                                               and c["expected"] != "post" for c in cases),
                        "gate_right": sum(c["gate"]["action"] == c["expected"] for c in cases)}}
    data["summary"]["agent_no_gate_cases"] = [
        c["title"].lower() for c in cases
        if c["without_gate"] and c["without_gate"]["posted"] and c["expected"] != "post"]
    name = "data.json" if lang == "tr" else f"data-{lang}.json"
    (SITE / name).write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{lang}: {len(cases)} cases, {len(clips)} clips -> site/{name}")


def complete(lang):
    """A language goes on the page once all six cases have both agent runs."""
    f = results(lang) / "agent_warehouse_cross.json"
    if not f.exists():
        return False
    rows = json.loads(f.read_text())
    if lang == "tr":
        return True
    variants = {r["variant"] for r in json.loads((results(lang) / "check_warehouse.json").read_text())}
    return all({r["variant"] for r in rows if r["gate"] == g} >= variants for g in (True, False))


LABEL = {"tr": "Türkçe", "en": "English", "de": "Deutsch", "zh": "中文"}


def main():
    built = [lang for lang in LANGS if complete(lang)]
    for lang in built:
        build(lang)
    # The page reads this list from data.json to offer the languages that have results.
    data = json.loads((SITE / "data.json").read_text())
    data["languages"] = [{"code": lang, "label": LABEL[lang],
                          "file": "data.json" if lang == "tr" else f"data-{lang}.json"}
                         for lang in built]
    (SITE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
