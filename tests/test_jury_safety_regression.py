"""Focused offline policy regressions prompted by 3 Nov new-input review.

These tests mock evidence. They do not rerun Meta models or establish held-out accuracy.
Run: python -m unittest tests/test_jury_safety_regression.py
"""
import unittest

from cbyp.gate import BLOCK, HUMAN, POST, decide


def fixture():
    note = {
        "supplier": "Fixture Supplier",
        "items": [{"description": "Widget Model A", "quantity": 1,
                   "unit": "carton", "legible": True}],
        "embedded_instructions": [],
    }
    camera = {
        "product_on_labels": "Widget Model A",
        "cartons_visible": 1, "damaged_cartons": 0,
        "stacked": False, "all_cartons_visible": True,
    }
    order = {
        "number": "TEST-PO-1", "product": "Widget Model A",
        "supplier": "Fixture Supplier", "require_supplier": True,
        "unit": "carton", "ordered": 1, "received": 0,
    }
    spoken = {"quantity": 1, "unit": "carton", "certain": True}
    second = {
        "supplier": "Fixture Supplier",
        "items": [dict(note["items"][0])],
        "embedded_instructions": [],
    }
    audit = {"ok": True, "quantity": True, "product": True, "instructions": ""}
    return dict(note=note, sam_confs=[0.95], look=camera, order=order,
                spoken=spoken, second=second, audit=audit)


class JurySafetyRegression(unittest.TestCase):
    def test_fully_matching_fixture_has_a_positive_control(self):
        result = decide(**fixture())
        self.assertEqual((result.action, result.rule, result.quantity),
                         (POST, "match", 1))

    def test_boundary_guard_overrides_otherwise_matching_evidence(self):
        for frame in (
            {"requires_review": True},
            {"requires_review": True, "error": "frame inspection unavailable"},
        ):
            with self.subTest(frame=frame):
                result = decide(**fixture(), frame=frame)
                self.assertEqual((result.action, result.rule),
                                 (HUMAN, "frame_boundary"))
                self.assertIsNone(result.quantity)

    def test_no_frame_warning_keeps_positive_control(self):
        result = decide(**fixture(), frame={"requires_review": False})
        self.assertEqual(result.action, POST)

    def test_independent_reader_disagreement_cannot_approve(self):
        values = fixture()
        values["second"]["items"][0]["description"] = "Widget Model B"
        result = decide(**values)
        self.assertEqual((result.action, result.rule),
                         (HUMAN, "readers_disagree"))

    def test_supplier_disagreement_cannot_approve(self):
        values = fixture()
        values["second"]["supplier"] = "Wrong Supplier"
        result = decide(**values)
        self.assertEqual((result.action, result.rule),
                         (HUMAN, "readers_disagree"))

    def test_camera_product_mismatch_is_not_approved(self):
        values = fixture()
        values["look"]["product_on_labels"] = "Widget Model B"
        result = decide(**values)
        self.assertEqual((result.action, result.rule),
                         (BLOCK, "wrong_product"))


if __name__ == "__main__":
    unittest.main()
