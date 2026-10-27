"""Run the perception side of the gate on every rendered warehouse variant.

Usage: .venv/bin/python experiments/check_warehouse.py [--sam-only] [variant ...]
--sam-only refreshes only the SAM fields of an existing results file (no Spark calls).
Reads experiments/blender/out/depo-<variant>-{kamera,irsaliye}.png and depo-truth.json,
writes experiments/results/check_warehouse.json.

Per variant:
  note     Spark reads the delivery note close-up (quantity, product, embedded instructions)
  sam      SAM 3.1 counts "cardboard box" and "damaged cardboard box" on the ceiling camera
  spark    Spark looks at the same frame: product on the labels, carton count, damage, stacking
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.delivery_note import read_note  # noqa: E402
from cbyp.perception import look, sam_confs  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import OUT, RAW, RES  # noqa: E402
def sam_fields(cam):
    out = {}
    for concept in ("cardboard box", "damaged cardboard box"):
        confs = sam_confs(cam, concept)
        out[concept], out[concept + " conf"] = len(confs), confs
    return out


def main(variants):
    truth = json.loads((OUT / "depo-truth.json").read_text())
    path = RES / "check_warehouse.json"
    # Saved after every case, so a timeout doesn't lose the finished ones; a rerun resumes.
    done = {r["variant"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    for v in variants or list(truth):
        if v in done and not variants:
            continue
        cam, note = OUT / f"depo-{v}-kamera.png", OUT / f"depo-{v}-irsaliye.png"
        claim = read_note(note)["claim"]
        row = {
            "variant": v, "truth": truth[v],
            "note": {"items": claim["items"], "embedded_instructions":
                     claim["embedded_instructions"]},
            "sam": sam_fields(cam),
            "spark": look(cam),
        }
        done[v] = row
        print(json.dumps({k: row[k] for k in ("variant", "sam", "spark")}, ensure_ascii=False),
              flush=True)
        print("   note:", [(i["quantity"], i["description"]) for i in claim["items"]],
              claim["embedded_instructions"], flush=True)
        rows = [done[k] for k in truth if k in done]
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2))


def refresh_sam(variants):
    path = RES / "check_warehouse.json"
    rows = json.loads(path.read_text())
    for row in rows:
        if not variants or row["variant"] in variants:
            row["sam"] = sam_fields(OUT / f"depo-{row['variant']}-kamera.png")
            print(row["variant"], row["sam"])
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--sam-only"]:
        refresh_sam(args[1:])
    else:
        main(args)
