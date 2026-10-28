"""Real photos: what Spark, SAM and the gate do outside Blender.

Usage: .venv/bin/python experiments/run_real.py
experiments/real/IMG_*.jpg: a stack of 18 flattened "DEPOZİTOLU KOLİ" cartons, photographed by
Sena on 28 Oct (top, side, low angle). Not a pallet of closed cartons: the hard case, sheets
whose edges run together. There is no delivery note, so the gate is asked with a note that
says the true number (18): the question is whether it would let that number through
unverified. Writes experiments/results/real_photos.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbyp.gate import decide, sam_bands  # noqa: E402
from cbyp.perception import look, sam_confs  # noqa: E402
from paths import results  # noqa: E402

HERE = Path(__file__).parent
TRUTH = 18
NOTE = {"items": [{"description": "Depozitolu koli", "quantity": TRUTH, "unit": "adet",
                   "legible": True}], "embedded_instructions": []}


def main():
    rows = []
    for path in sorted((HERE / "real").glob("IMG_*.jpg")):
        seen = look(path)
        confs = {c: sam_confs(path, c) for c in ("cardboard box", "flattened cardboard")}
        best = max(confs.values(), key=lambda cs: (sam_bands(cs)[0], len(cs)))
        d = decide(NOTE, best, seen | {"product_on_labels": "Depozitolu koli"})
        rows.append({"photo": path.name, "truth": TRUTH, "spark": seen,
                     "sam": {c: dict(zip(("sure", "doubtful"), sam_bands(cs)))
                             for c, cs in confs.items()},
                     "gate": [d.action, d.rule], "reason": d.reasons[0]})
        print(path.name, seen["cartons_visible"], seen["stacked"], rows[-1]["sam"], d.action,
              d.rule, flush=True)
    (results("tr") / "real_photos.json").write_text(json.dumps(rows, ensure_ascii=False,
                                                                 indent=2))


if __name__ == "__main__":
    main()
