"""Run the perception side of the gate on every rendered warehouse variant.

Usage: .venv/bin/python experiments/check_warehouse.py [variant ...]
Reads experiments/blender/out/depo-<variant>-{kamera,irsaliye}.png and depo-truth.json,
writes experiments/results/check_warehouse.json.

Per variant:
  note     Spark reads the delivery note close-up (quantity, product, embedded instructions)
  sam      SAM 3.1 counts "cardboard box" and "damaged cardboard box" on the ceiling camera
  spark    Spark looks at the same frame: product on the labels, carton count, damage, stacking
"""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.delivery_note import read_note  # noqa: E402
from cbyp.meta import SPARK, client  # noqa: E402
from cbyp.sam import parse, segment_image  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "blender" / "out"
MIN_CONF = 0.7

LOOK = {
    "type": "object", "additionalProperties": False,
    "required": ["product_on_labels", "cartons_visible", "damaged_cartons", "stacked",
                 "all_cartons_visible"],
    "properties": {
        "product_on_labels": {"type": "string"},
        "cartons_visible": {"type": "integer"},
        "damaged_cartons": {"type": "integer"},
        "stacked": {"type": "boolean", "description": "Cartons stacked in more than one layer."},
        "all_cartons_visible": {"type": "boolean",
                                "description": "False if some cartons may be hidden from view."},
    },
}
LOOK_PROMPT = (
    "Ceiling camera view of a pallet at a warehouse receiving dock. Read the product name "
    "printed on the carton labels exactly as written, count the cartons, count cartons that "
    "look crushed, wet or torn, and say whether cartons are stacked so some may be hidden."
)


def look(path):
    url = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "pallet", "strict": True, "schema": LOOK}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": LOOK_PROMPT},
            {"type": "image_url", "image_url": {"url": url}}]}],
    )
    return json.loads(r.choices[0].message.content)


def sam_count(path, concept):
    return sum((d.conf or 0) >= MIN_CONF for d in parse(segment_image(path, concept)))


def main(variants):
    truth = json.loads((OUT / "depo-truth.json").read_text())
    rows = []
    for v in variants or list(truth):
        cam, note = OUT / f"depo-{v}-kamera.png", OUT / f"depo-{v}-irsaliye.png"
        claim = read_note(note)["claim"]
        row = {
            "variant": v, "truth": truth[v],
            "note": {"items": claim["items"], "embedded_instructions":
                     claim["embedded_instructions"]},
            "sam": {"cardboard box": sam_count(cam, "cardboard box"),
                    "damaged cardboard box": sam_count(cam, "damaged cardboard box")},
            "spark": look(cam),
        }
        rows.append(row)
        print(json.dumps({k: row[k] for k in ("variant", "sam", "spark")}, ensure_ascii=False))
        print("   note:", [(i["quantity"], i["description"]) for i in claim["items"]],
              claim["embedded_instructions"])
    (HERE / "results" / "check_warehouse.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
