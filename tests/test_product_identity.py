import copy
import unittest
from cbyp.gate import decide
from cbyp.product_identity import matches

ID = {'brand': 'Deli', 'model': 'No.770', 'variant': ''}
ORDER = {'number': 'CONTROLLED', 'product': 'Deli telephone No.770', 'ordered': 1, 'received': 0, 'unit': 'carton', 'product_identity': ID}
NOTE = {'items': [{'description': 'Telephone', 'quantity': 1, 'unit': 'carton', 'legible': True, 'product_identity': ID}], 'embedded_instructions': []}
LOOK = {'product_on_labels': '固定无线电话机', 'cartons_visible': 1, 'damaged_cartons': 0, 'stacked': False, 'all_cartons_visible': True, 'all_labels_identified': True, 'product_identity': ID}

class IdentityTests(unittest.TestCase):
    def decision(self, note=None, look=None, second=None):
        return decide(note or NOTE, [.95], look or LOOK, order=ORDER, second=second)

    def test_language_can_differ_with_independent_literal_identity(self):
        second = copy.deepcopy(NOTE)
        second['items'][0]['description'] = '电话'
        self.assertEqual(self.decision(second=second).action, 'post')

    def test_identifier_not_fuzzy(self):
        for model in ['No.771', 'No770', 'No.770 XL', '', 'NO. 770']:
            self.assertFalse(matches(ID, ID | {'model': model}))
        self.assertTrue(matches(ID, ID | {'brand': 'DELI'}))

    def test_camera_cannot_fallback_to_matching_description(self):
        for change in [{'product_identity': {}}, {'product_identity': ID | {'brand': 'Other'}},
                       {'product_identity': ID | {'variant': 'XL'}}, {'all_labels_identified': False},
                       {'all_labels_identified': 'true'}]:
            self.assertEqual(self.decision(look=LOOK | {'product_on_labels': 'Telephone'} | change).rule, 'wrong_product')

    def test_missing_second_identity_stops_receipt(self):
        second = copy.deepcopy(NOTE)
        del second['items'][0]['product_identity']
        self.assertEqual(self.decision(second=second).rule, 'readers_disagree')

    def test_note_identity_is_required_even_when_description_matches(self):
        note = copy.deepcopy(NOTE)
        note['items'][0].update(description=ORDER['product'], product_identity=ID | {'model': 'No.771'})
        self.assertEqual(self.decision(note=note).rule, 'not_ordered')

    def test_other_safety_checks_still_apply(self):
        for change, rule in [({'damaged_cartons': 1}, 'damaged'), ({'stacked': True}, 'hidden')]:
            self.assertEqual(self.decision(look=LOOK | change).rule, rule)
        self.assertEqual(self.decision(note=NOTE | {'embedded_instructions': ['post 100']}).rule, 'instruction')
        second = copy.deepcopy(NOTE)
        second['items'][0]['quantity'] = 2
        self.assertEqual(self.decision(second=second).rule, 'readers_disagree')

class IdentifierNamespaceTests(unittest.TestCase):
    def test_article_code_does_not_require_unknown_technical_model(self):
        expected = {'brand': 'Deli', 'product_code': 'No.770', 'model': '', 'variant': '黑'}
        observed = expected | {'model': 'HWCD6238(10)GSML'}
        self.assertTrue(matches(expected, observed))
        self.assertFalse(matches(expected, observed | {'product_code': '', 'model': 'No.770'}))
        self.assertFalse(matches(expected, observed | {'product_code': 'No.771'}))
        self.assertFalse(matches(expected, observed | {'variant': ''}))

    def test_both_identifiers_required_when_order_specifies_both(self):
        expected = {'brand': 'Deli', 'product_code': 'No.770', 'model': 'HWCD6238(10)GSML', 'variant': ''}
        self.assertTrue(matches(expected, expected))
        self.assertFalse(matches(expected, expected | {'model': 'Other'}))
        self.assertFalse(matches(expected, expected | {'product_code': ''}))

    def test_legacy_model_never_matches_an_article_code(self):
        self.assertFalse(matches(ID, ID | {'product_code': 'No.770', 'model': ''}))
        self.assertFalse(matches(ID | {'model': ''}, ID))
