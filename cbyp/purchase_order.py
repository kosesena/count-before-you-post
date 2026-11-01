"""Purchase orders: the third side of a goods receipt.

In an ERP a goods receipt is posted against what the company ordered, not only against what
the supplier's note says. The purchase order, the delivery note and the counted quantity must
agree: the three-way match at receiving. The gate reads the order from the company's own
records, never from the agent or the note.

These are our own order records for the dock's deliveries, one per language: each delivery
was ordered as 12 cartons of the product on its note, from the supplier on its note. The
ERPNext run keeps a real Purchase Order for the same line (erpnext.Client.ensure_order).
"""

ORDERED = 12

ORDERS = {
    "tr": {"number": "PO-2026-1047", "supplier": "Doğan Gıda Pazarlama",
           "product": "Ayçiçek yağı 5 L"},
    "en": {"number": "PO-2026-1048", "supplier": "Harbor Foods Ltd",
           "product": "Sunflower oil 5 L"},
    "de": {"number": "PO-2026-1049", "supplier": "Sonnenfeld Lebensmittel GmbH",
           "product": "Sonnenblumenöl 5 L"},
    "zh": {"number": "PO-2026-1050", "supplier": "海港食品有限公司",
           "product": "葵花籽油 5升"},
}


def order_for(lang: str = "tr", ordered: int = ORDERED, received: int = 0) -> dict:
    """The open order line a delivery in this language is received against."""
    return {**ORDERS[lang], "ordered": ordered, "received": received, "unit": "carton"}


def open_quantity(order: dict) -> int:
    """What may still be received on the order line."""
    return max(0, order["ordered"] - order.get("received", 0))
