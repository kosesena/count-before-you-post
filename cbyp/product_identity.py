"""Literal identity evidence; never inferred translations or fuzzy model matching."""
import unicodedata

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["brand", "model", "variant"],
    "properties": {key: {"type": "string"} for key in ("brand", "model", "variant")},
}
PROMPT = (
    " Copy product_identity brand, model and variant literally from visible text. "
    "Use empty strings for missing or unreadable fields. Never infer a brand/model from "
    "appearance, translate identifiers, or use external knowledge. Variant means an explicit "
    "size/capacity/colour/pack specification; do not omit a visible variant. "
)

def literal(value):
    # Preserve punctuation, internal whitespace and diacritics in identifiers.
    return unicodedata.normalize("NFC", value).strip().casefold() if isinstance(value, str) else ""

def valid(identity):
    return (isinstance(identity, dict) and set(identity) == {"brand", "model", "variant"}
            and all(isinstance(v, str) for v in identity.values())
            and bool(literal(identity["brand"]) and literal(identity["model"])))

def matches(expected, observed):
    return (valid(expected) and valid(observed)
            and all(literal(expected[k]) == literal(observed[k]) for k in expected))
