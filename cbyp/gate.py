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
  SAM and Spark disagree         -> human   (carton by carton when a cross-check is given)
  receiver unsure or says other  -> human   (when a spoken count is given)
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

# Words the agent may ask SAM to look for. "fruit crate" returned 0 on a photo full of fruit
# crates, so the agent can retry with another word, but only from this list: "box" alone also
# picks up plastic crates.
CONCEPTS = ("cardboard box", "carton", "shipping box", "package")

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


def cross_count(cross) -> int | None:
    """The count a carton-by-carton cross-check supports, or None.

    Every carton must be found by both models. A carton only SAM sees is tolerated when SAM
    was doubtful about it (the gap in the short delivery, at 0.81); one SAM is sure of is not.
    """
    if cross.spark_only or cross.doubled or any(c >= SURE for c in cross.sam_only_conf):
        return None
    return len(cross.agreed)


def decide(note: dict, sam_confs: list[float], look: dict, cross=None,
           spoken: dict | None = None) -> Decision:
    """cross: an optional crosscheck.CrossCheck; when given it replaces the count bands.
    spoken: an optional voice.understand() result, the receiver's own count."""
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
    if cross is not None:
        evidence["cross"] = {"agreed": len(cross.agreed), "sam_only": len(cross.sam_only),
                             "spark_only": len(cross.spark_only), "doubled": len(cross.doubled)}
        count = cross_count(cross)
        if count is None:
            return out(HUMAN, "SAM and Spark disagree on which objects are cartons: "
                       f"{len(cross.agreed)} agreed, {len(cross.sam_only)} only SAM, "
                       f"{len(cross.spark_only)} only Spark.")
    else:
        count = agreed_count(sam_confs, look["cartons_visible"])
        if count is None:
            return out(HUMAN, f"SAM ({sure} sure, {doubtful} doubtful) and Spark "
                       f"({look['cartons_visible']}) disagree on the count.")
    if spoken is not None:
        evidence["spoken"] = spoken
        if not spoken.get("certain", False) or spoken.get("quantity") is None:
            return out(HUMAN, "The receiver was not sure of the count.", count)
        if spoken["quantity"] != count:
            return out(HUMAN, f"The receiver said {spoken['quantity']}, the camera "
                       f"counted {count}.", count)
    if count == item["quantity"]:
        return out(POST, f"Note, SAM and Spark agree on {count}.", count)
    return out(BLOCK, f"Counted {count}, note says {item['quantity']}; draft a "
               f"discrepancy for the supplier.", count)
