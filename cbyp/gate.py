"""The gate: decides whether a goods receipt may be written to the ERP.

Inputs are three independent readings of one delivery:
  note   what Spark read on the delivery note (read_note()["claim"])
  sam    SAM 3.1 detections of "cardboard box" on the ceiling camera, as confidences
  look   what Spark saw on the same frame (product, count, damage, stacking)

The gate is plain code, not a model: no text on the note or in a model answer can
change a rule. Rules run in order and the first one that fires decides.

  instruction on the note        -> block   (never follow it; quantity stays from the table)
  note unreadable                -> human
  label product != note product  -> block
  stacked / cartons hidden       -> human   (count cannot be verified)
  damaged cartons                -> human   (propose partial receipt of the intact ones)
  SAM and Spark disagree         -> human
  agreed count == note           -> post
  agreed count != note           -> block   (draft a discrepancy for the supplier)
"""
import unicodedata
from dataclasses import dataclass, field

POST, BLOCK, HUMAN = "post", "block", "human"

# SAM's wrong detections came back lower than its true ones (a gap read as a carton at
# 0.81; real cartons 0.90-0.92), so detections are split into two bands.
SURE = 0.88
MIN_CONF = 0.7

_TR = str.maketrans({"İ": "i", "I": "ı"})


def normalize(text: str) -> str:
    """Compare product names across Turkish case and diacritics ('YAĞI' == 'yagi')."""
    text = text.translate(_TR).casefold().replace("ı", "i")
    text = "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c))
    return " ".join("".join(c if c.isalnum() else " " for c in text).split())


def same_product(a: str, b: str) -> bool:
    a, b = normalize(a), normalize(b)
    return bool(a and b) and (a == b or a in b or b in a)


@dataclass
class Decision:
    action: str                      # post | block | human
    quantity: int | None             # what would be written (post) or proposed (human)
    reasons: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


def sam_bands(confs: list[float]) -> tuple[int, int]:
    """(sure, doubtful) detection counts."""
    sure = sum(c >= SURE for c in confs)
    return sure, sum(MIN_CONF <= c < SURE for c in confs)


def agreed_count(sam_confs: list[float], spark_count: int) -> int | None:
    """The count both perceptions support, or None if they disagree.

    Spark agrees with SAM when it lands between SAM's sure count and sure + doubtful:
    the doubtful detections are exactly the ones SAM may have imagined (or missed).
    """
    sure, doubtful = sam_bands(sam_confs)
    return spark_count if sure <= spark_count <= sure + doubtful else None


def decide(note: dict, sam_confs: list[float], look: dict) -> Decision:
    items = note.get("items") or []
    sure, doubtful = sam_bands(sam_confs)
    evidence = {"note": [(i["quantity"], i["description"]) for i in items],
                "sam_sure": sure, "sam_doubtful": doubtful,
                "spark_count": look["cartons_visible"], "label": look["product_on_labels"]}

    def out(action, reason, qty=None):
        return Decision(action, qty, [reason], evidence)

    if note.get("embedded_instructions"):
        return out(BLOCK, "The note contains instructions to software; not followed. "
                   "Supervisor notified: " + " | ".join(note["embedded_instructions"]))
    if len(items) != 1 or not items[0].get("legible", False):
        return out(HUMAN, "Delivery note has no single legible line item.")
    item = items[0]
    if not same_product(look["product_on_labels"], item["description"]):
        return out(BLOCK, f"Wrong product: labels say '{look['product_on_labels']}', "
                   f"note says '{item['description']}'.")
    if look["stacked"] or not look["all_cartons_visible"]:
        return out(HUMAN, "Cartons are stacked or hidden; the count cannot be verified "
                   "from the camera.")
    if look["damaged_cartons"] > 0:
        intact = look["cartons_visible"] - look["damaged_cartons"]
        return out(HUMAN, f"{look['damaged_cartons']} damaged carton(s); propose partial "
                   f"receipt of {intact}.", intact)
    count = agreed_count(sam_confs, look["cartons_visible"])
    if count is None:
        return out(HUMAN, f"SAM ({sure} sure, {doubtful} doubtful) and Spark "
                   f"({look['cartons_visible']}) disagree on the count.")
    if count == item["quantity"]:
        return out(POST, f"Note, SAM and Spark agree on {count}.", count)
    return out(BLOCK, f"Counted {count}, note says {item['quantity']}; draft a "
               f"discrepancy for the supplier.", count)
