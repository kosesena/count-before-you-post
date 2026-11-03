"""The gate: decides whether a goods receipt may be written to the ERP.

Inputs are three independent readings of one delivery:
  note   what Spark read on the delivery note (read_note()["claim"])
  sam    SAM 3.1 detections of "cardboard box" on the ceiling camera, as confidences
  look   what Spark saw on the same frame (product, count, damage, stacking)
and, from the company's own records, the purchase order line it is received against
(purchase_order.order_for): the order, the note and the count must agree.

The gate is plain code, not a model: no text on the note or in a model answer can
change a rule. Rules run in order and the first one that fires decides.

  instruction on the note        -> block   (never follow it; quantity stays from the table)
  invisible text in a PDF note   -> human   (white or tiny text no person and no Spark saw)
  note unreadable                -> human
  note product not on the order  -> block   (not what we ordered: refuse it at the dock)
  label product != note product  -> block   (wrong product: refuse it at the dock)
  stacked / cartons hidden       -> human   (count cannot be verified)
  damaged cartons                -> human   (propose partial receipt of the intact ones)
  SAM and Spark disagree         -> human   (carton by carton when a cross-check is given)
  receiver unsure or says other  -> human   (when a spoken count is given)
  count above the order's open   -> human   (over-delivery: receive what was ordered, or
    quantity                                 return the rest; the supervisor decides)
  second reading disagrees       -> human   (only before a post: the open-weight second
                                             reader saw another line, quantity or product,
                                             or an instruction Spark did not report)
  Wonder can't confirm the note  -> human   (only before a post: Muse Wonder checks Spark's
                                             reading against the note, quoting it)
  agreed count == note           -> post
  agreed count != note           -> block   (draft a discrepancy for the supplier)
"""
import unicodedata
from dataclasses import dataclass, field

from .purchase_order import open_quantity
from .product_identity import matches as identity_matches

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
    # Labels break words where notes don't ("SONNEN-BLUMENÖL", "葵花籽油 5 升"): compare
    # without spaces too.
    ca, cb = a.replace(" ", ""), b.replace(" ", "")
    return bool(a and b) and (a == b or ca == cb)


# Explicit aliases, never substring matching or guessed pack conversions.
UNIT_ALIASES = {
    "carton": {"koli", "koliler", "carton", "cartons", "box", "boxes", "karton", "kartons", "箱"},
    "piece": {"adet", "nos", "unit", "units", "piece", "pieces", "stuck", "stück", "个"},
    "litre": {"l", "litre", "liter", "litres", "liters", "升"},
}


def canonical_unit(value):
    value = normalize(value) if isinstance(value, str) else ""
    return next((key for key, aliases in UNIT_ALIASES.items()
                 if value in {normalize(x) for x in aliases}), None)


@dataclass
class Decision:
    action: str                      # post | block | human
    quantity: int | None             # what would be written (post) or proposed (human)
    reasons: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)
    rule: str = ""                   # which rule decided, one of RULES


# The rules in the order they run; Decision.rule names the one that fired.
RULES = ("instruction", "invisible_text", "unreadable", "invalid_quantity", "unit", "frame_boundary", "supplier", "not_ordered", "wrong_product", "hidden",
         "damaged", "disagree", "receiver", "over_order", "readers_disagree", "audit", "match",
         "mismatch")


def differences(first: dict, second: dict, identity=None) -> list[str]:
    """Where two readings of one note disagree on anything the gate decides with."""
    a, b = first.get("items") or [], second.get("items") or []
    if len(a) != len(b):
        return [f"{len(a)} line item(s) against {len(b)}"]
    out = []
    for x, y in zip(a, b):
        if x["quantity"] != y["quantity"]:
            out.append(f"quantity {x['quantity']} against {y['quantity']}")
        if canonical_unit(x.get("unit")) != canonical_unit(y.get("unit")):
            out.append("unit differs between readers")
        if not (identity_matches(identity, y.get("product_identity")) if identity is not None
                else same_product(x["description"], y["description"])):
            out.append(f"product '{x['description']}' against '{y['description']}'")
        if x.get("legible", False) != y.get("legible", False):
            out.append("one reader found the quantity hard to read")
    return out


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
           spoken: dict | None = None, invisible: list[str] | None = None,
           second: dict | None = None, audit: dict | None = None,
           order: dict | None = None, frame: dict | None = None) -> Decision:
    """cross: an optional crosscheck.CrossCheck; when given it replaces the count bands.
    spoken: an optional voice.understand() result, the receiver's own count.
    invisible: pdf_text.invisible_lines() of a PDF note, found in code, not by Spark.
    second: the open-weight second reader's claim on the same note (second_reader).
    audit: Muse Wonder's check of Spark's reading against the note (wonder.audit_note).
    order: the purchase order line from the company's records (purchase_order.order_for)."""
    items = note.get("items") or []
    sure, doubtful = sam_bands(sam_confs)
    evidence = {"note": [(i["quantity"], i["description"]) for i in items],
                "sam_sure": sure, "sam_doubtful": doubtful,
                "spark_count": look["cartons_visible"], "label": look["product_on_labels"]}

    def out(rule, action, reason, qty=None):
        return Decision(action, qty, [reason], evidence, rule)

    if note.get("embedded_instructions"):
        return out("instruction", BLOCK, "The note contains instructions to software; not followed. "
                   "Supervisor notified: " + " | ".join(note["embedded_instructions"]))
    if invisible:
        evidence["invisible"] = invisible
        return out("invisible_text", HUMAN, "The PDF note carries text no one can see (white or "
                   "under 4 pt); the supervisor reads it first: " + " | ".join(invisible))
    if len(items) != 1 or not items[0].get("legible", False):
        return out("unreadable", HUMAN, "Delivery note has no single legible line item.")
    item = items[0]
    quantities = [item.get("quantity"), look.get("cartons_visible"), look.get("damaged_cartons")]
    if any(type(q) is not int or q < 0 for q in quantities) or item["quantity"] == 0 or look["damaged_cartons"] > look["cartons_visible"]:
        return out("invalid_quantity", HUMAN, "Invalid or empty quantity evidence; check the delivery.")
    expected_unit = canonical_unit(order.get("unit", "carton")) if order else "carton"
    if expected_unit != "carton" or canonical_unit(item.get("unit")) != expected_unit:
        return out("unit", HUMAN, "Camera counts cartons. Note and order must explicitly use cartons; no pack conversion is inferred.")
    if frame is not None:
        evidence["frame_completeness"] = frame
        if frame.get("requires_review"):
            if frame.get("error"):
                return out("frame_boundary", HUMAN,
                           "Frame completeness could not be verified; retry the check before receiving.")
            return out("frame_boundary", HUMAN,
                       "A detected carton touches the image boundary guard band; complete carton extent "
                       "is not verified. Supply a wider view or request human review.")
    if order is not None and order.get("require_supplier"):
        if not note.get("supplier") or normalize(note["supplier"]) != normalize(order.get("supplier", "")):
            return out("supplier", BLOCK, "Supplier on the note does not exactly match the trusted purchase order.")
    identity = order.get("product_identity") if order else None
    use_identity = order is not None and "product_identity" in order
    if use_identity:
        evidence["product_identity"] = {"expected": identity, "note": item.get("product_identity"),
                                        "camera": look.get("product_identity"),
                                        "all_labels_identified": look.get("all_labels_identified", False)}
    if order is not None:
        evidence["order"] = {"number": order["number"], "product": order["product"],
                             "ordered": order["ordered"], "open": open_quantity(order)}
        if use_identity and not identity_matches(identity, item.get("product_identity")):
            return out("not_ordered", BLOCK, "Note brand/article code/technical model/variant does not verify the trusted order identity. "
                       "No receipt; compare the identifier evidence before deciding whether to return the load.")
        if not use_identity and not same_product(order["product"], item["description"]):
            return out("not_ordered", BLOCK, f"Not on the order: {order['number']} is for "
                       f"'{order['product']}', the note says '{item['description']}'. Refuse it "
                       "at the dock; the load goes back on the truck.")
    camera_matches = (identity_matches(identity, look.get("product_identity"))
                      and look.get("all_labels_identified") is True) if use_identity else same_product(
                          look["product_on_labels"], item["description"])
    if not camera_matches:
        detail = ("Every carton must have a readable, matching brand/article code/technical model/variant."
                  if use_identity else f"Camera read '{look['product_on_labels']}', note says '{item['description']}'.")
        return out("wrong_product", BLOCK, f"Product identity not verified. {detail} "
                   "No receipt; check the exact product and model on the labels before deciding whether to return the load.")
    if look["stacked"] or not look["all_cartons_visible"]:
        return out("hidden", HUMAN, "Cartons are stacked or hidden; the count cannot be verified "
                   "from the camera.")
    if look["damaged_cartons"] > 0:
        intact = look["cartons_visible"] - look["damaged_cartons"]
        return out("damaged", HUMAN, f"{look['damaged_cartons']} damaged carton(s); propose partial "
                   f"receipt of {intact}.", intact)
    if cross is not None:
        evidence["cross"] = {"agreed": len(cross.agreed), "sam_only": len(cross.sam_only),
                             "spark_only": len(cross.spark_only), "doubled": len(cross.doubled)}
        count = cross_count(cross)
        if count is None:
            return out("disagree", HUMAN, "SAM and Spark disagree on which objects are cartons: "
                       f"{len(cross.agreed)} agreed, {len(cross.sam_only)} only SAM, "
                       f"{len(cross.spark_only)} only Spark.")
    else:
        count = agreed_count(sam_confs, look["cartons_visible"])
        if count is None:
            return out("disagree", HUMAN, f"SAM ({sure} sure, {doubtful} doubtful) and Spark "
                       f"({look['cartons_visible']}) disagree on the count.")
    if spoken is not None:
        evidence["spoken"] = spoken
        if "unit" in spoken and canonical_unit(spoken["unit"]) != "carton":
            return out("receiver", HUMAN, "Receiver count must explicitly refer to cartons, not another or unknown unit.", count)
        if not spoken.get("certain", False) or type(spoken.get("quantity")) is not int or spoken["quantity"] < 0:
            return out("receiver", HUMAN, "The receiver was not sure of the count.", count)
        if spoken["quantity"] != count:
            return out("receiver", HUMAN, f"The receiver said {spoken['quantity']}, the camera "
                       f"counted {count}.", count)
    if order is not None and count > open_quantity(order):
        left = open_quantity(order)
        return out("over_order", HUMAN, f"Over-delivery: counted {count}, {order['number']} has "
                   f"{left} open. The supervisor receives {left} and returns the rest, or asks "
                   "purchasing to raise the order.", left)
    if count == item["quantity"] and second is not None:
        # Asked only here, before a write: an open-weight reading is noisier than Spark's
        # (experiments/results/second_reader.json), so it may stop a receipt, never decide one.
        evidence["second_reader"] = [(i["quantity"], i["description"])
                                     for i in second.get("items") or []]
        diffs = differences(note, second, identity=identity if use_identity else None)
        if use_identity and not all(identity_matches(identity, i.get("product_identity"))
                                    for i in second.get("items") or []):
            diffs.append("second reader cannot verify trusted brand/article code/technical model/variant")
        if order is not None and order.get("require_supplier"):
            evidence["second_supplier"] = second.get("supplier", "")
            if not isinstance(second.get("supplier"), str) or not second["supplier"].strip() or normalize(second["supplier"]) != normalize(order.get("supplier", "")):
                diffs.append("second reader supplier does not match the trusted order")
        if second.get("embedded_instructions"):
            diffs.append("it reports an instruction to software: "
                         + " | ".join(second["embedded_instructions"]))
        if diffs:
            return out("readers_disagree", HUMAN, "Before posting, the second reader of the note "
                       "disagrees with Spark: " + "; ".join(diffs) + ".", count)
    if count == item["quantity"] and audit is not None:
        evidence["audit"] = audit
        if not audit["ok"]:
            problems = [f"{k} not supported by the note" for k in ("quantity", "product")
                        if not audit[k]]
            if audit["instructions"]:
                problems.append(f"the note carries an instruction: {audit['instructions']}")
            return out("audit", HUMAN, "Before posting, Wonder could not confirm Spark's reading "
                       "of the note: " + "; ".join(problems) + ".", count)
    if count == item["quantity"]:
        on_order = f" Within {order['number']} ({open_quantity(order)} open)." if order else ""
        return out("match", POST, f"Note, SAM and Spark agree on {count}.{on_order}", count)
    return out("mismatch", BLOCK, f"Counted {count}, note says {item['quantity']}; draft a "
               f"discrepancy for the supplier.", count)
