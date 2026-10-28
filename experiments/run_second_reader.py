"""Open-weight second readers on every delivery note, and what the gate does with them.

Usage: .venv/bin/python experiments/run_second_reader.py [baseten]
Muse Glimmer and Muse Spark Open (through OpenRouter) read the 24 dock notes (6 cases x 4
languages) and the 3 PDF notes with Spark's own schema and prompt. Each reading is compared
with Spark's (recorded in results/<lang>/check_warehouse.json) and with the truth, and the gate
decides again with the second reading added. Writes experiments/results/second_reader.json,
saved after every note so a dropped connection loses nothing. The first run, before the
hosts were pinned and Glimmer got its recommended sampling, is second_reader_v1.json.
With `baseten`, only Spark Open, on Baseten (needs BASETEN_API_KEY), into
second_reader_baseten.json, to compare the same model on another host.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbyp.delivery_note import read_note as spark_read  # noqa: E402
from cbyp.gate import decide, differences  # noqa: E402
from cbyp.pdf_text import invisible_lines  # noqa: E402
from cbyp.second_reader import GLIMMER, SPARK_OPEN, read_note  # noqa: E402
from paths import LANGS, out, results  # noqa: E402
from run_gate import cached_cross  # noqa: E402

HERE = Path(__file__).parent
BASETEN_RUN = "baseten" in sys.argv[1:]
RESULT = results("tr") / ("second_reader_baseten.json" if BASETEN_RUN else "second_reader.json")
MODELS = (SPARK_OPEN,) if BASETEN_RUN else (GLIMMER, SPARK_OPEN)


def notes():
    """(lang, case, note path, Spark's claim, camera evidence, truth) for every note."""
    for lang in LANGS:
        for p in json.loads((results(lang) / "check_warehouse.json").read_text()):
            v = p["variant"]
            ev = (p["sam"]["cardboard box conf"], p["spark"], cached_cross(v, results(lang) / "sam_raw"))
            yield (lang, v, out(lang) / f"depo-{v}-irsaliye.png", p["note"], ev,
                   {"quantity": 12, "injection": v == "talimat"})
    ok = next(p for p in json.loads((results("tr") / "check_warehouse.json").read_text())
              if p["variant"] == "ok")
    ev = (ok["sam"]["cardboard box conf"], ok["spark"], cached_cross("ok", results("tr") / "sam_raw"))
    truth = json.loads((HERE / "notes" / "pdf-truth.json").read_text())
    for name, t in truth.items():
        path = HERE / "notes" / f"{name}.pdf"
        yield ("tr", name, path, spark_read(path)["claim"], ev,
               {"quantity": t["quantity"], "injection": t["injection"]})


def main():
    if BASETEN_RUN:
        from cbyp.second_reader import host
        assert host(SPARK_OPEN) == "baseten", "BASETEN_API_KEY is not set"
    rows = json.loads(RESULT.read_text()) if RESULT.exists() else []
    done = {(r["lang"], r["case"], r["model"]) for r in rows}
    for lang, case, path, spark, (confs, look, cross), truth in notes():
        hidden = invisible_lines(path)
        alone = decide(spark, confs, look, cross, invisible=hidden)
        for model in MODELS:
            if (lang, case, model) in done:
                continue
            try:
                r = read_note(path, model=model)
            except Exception as e:  # recorded, not fatal: the next note still runs
                rows.append({"lang": lang, "case": case, "model": model,
                             "error": f"{type(e).__name__}: {e}"})
                RESULT.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
                print(f"{lang} {case:12} {model:22} ERROR {e}", flush=True)
                continue
            claim = r["claim"]
            both = decide(spark, confs, look, cross, invisible=hidden, second=claim)
            items = claim.get("items") or []
            rows.append({
                "lang": lang, "case": case, "model": model, "seconds": r["seconds"],
                "provider": r.get("provider"), "tries": r.get("tries"),
                "claim": claim, "differs_from_spark": differences(spark, claim),
                "quantity_right": len(items) == 1 and items[0]["quantity"] == truth["quantity"],
                "injection_seen": bool(claim.get("embedded_instructions")),
                "injection_truth": truth["injection"],
                "gate_spark_only": [alone.action, alone.rule],
                "gate_with_second": [both.action, both.rule]})
            RESULT.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
            x = rows[-1]
            print(f"{lang} {case:12} {model:22} qty_ok={x['quantity_right']!s:5} "
                  f"inj={x['injection_seen']!s:5}/{truth['injection']!s:5} "
                  f"diff={x['differs_from_spark']} gate {alone.action}->{both.action}", flush=True)


if __name__ == "__main__":
    main()
