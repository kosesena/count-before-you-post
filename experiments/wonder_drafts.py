"""Muse Wonder drafts the paperwork for every dock case the gate did not post.

Usage: [CBYP_LANG=en|de|zh] .venv/bin/python experiments/wonder_drafts.py
Reads the recorded readings (check_warehouse.json) and the cached cross-check, runs the gate
(no API calls), and asks Wonder only for refused or escalated cases. Writes wonder_drafts.json
to the language's results folder. Drafts are written in the delivery note's language.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from cbyp.gate import MIN_CONF, SURE, decide  # noqa: E402
from cbyp.wonder import draft  # noqa: E402
from paths import LANG, RES  # noqa: E402
from run_gate import cached_cross  # noqa: E402

LANGUAGE = {"tr": "Turkish", "en": "English", "de": "German", "zh": "Chinese"}[LANG]


def main():
    rows = []
    for p in json.loads((RES / "check_warehouse.json").read_text()):
        v, confs = p["variant"], p["sam"]["cardboard box conf"]
        cross = cached_cross(v)
        d = decide(p["note"], confs, p["spark"], cross)
        evidence = {"sam_sure": sum(c >= SURE for c in confs),
                    "sam_doubtful": sum(MIN_CONF <= c < SURE for c in confs),
                    "spark_look": p["spark"],
                    "carton_by_carton": cross and {"agreed": len(cross.agreed),
                                                   "only_sam": len(cross.sam_only),
                                                   "only_spark": len(cross.spark_only)}}
        start = time.perf_counter()
        doc = draft(d, p["note"], evidence, language=LANGUAGE)
        rows.append({"variant": v, "action": d.action, "rule": d.rule, "draft": doc,
                     "seconds": round(time.perf_counter() - start, 1)})
        print(v, d.action, d.rule, "->", doc and doc["document"], flush=True)
        if doc:
            print("  ", doc["title"], "|", doc["body"][:160].replace("\n", " "), flush=True)
    (RES / "wonder_drafts.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
