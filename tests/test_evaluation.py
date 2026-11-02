import json
import tempfile
import unittest
from pathlib import Path
from cbyp.evaluation import summarize, freeze

class Evaluation(unittest.TestCase):
    def test_policy_violation_is_not_physical_quantity_error(self):
        r=summarize([{'truth':{'action':'block','quantity':12},'result':{'action':'post','quantity':12}}])
        self.assertEqual(r['unsafe_accept'],1);self.assertEqual(r['quantity_errors'],0)
        self.assertIsNone(r['total_cost_usd'])
    def test_unnecessary_review_has_clean_denominator(self):
        r=summarize([{'truth':{'action':'post','quantity':12},'result':{'action':'human','quantity':12}}])
        self.assertEqual(r['unnecessary_review'],1);self.assertEqual(r['automatic_correct_accept_rate'],0)
    def test_seal_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'input').write_bytes(b'fixture')
            m={'cases':[{'id':'one','split':'held_out','truth':{'action':'post','quantity':1},'note':'input','camera':'input','audio':'input'}]}
            (p/'manifest').write_text(json.dumps(m));freeze(p/'manifest',p/'seal')
            with self.assertRaises(FileExistsError):freeze(p/'manifest',p/'seal')

    def test_physical_count_assessed_even_when_held(self):
        r=summarize([{'truth':{'action':'human','quantity':10,'physical_count':12},'result':{'action':'human','quantity':10},'observed_count':10}])
        self.assertEqual(r['physical_count_errors'],1)
        self.assertEqual(r['physical_count_assessed'],1)
        self.assertEqual(r['unsafe_accept'],0)
    def test_error_is_not_correct_hold(self):
        r=summarize([{'truth':{'action':'human'},'result':{'action':'error'}}])
        self.assertEqual(r['technical_failures'],1)
        self.assertEqual(r['correct_hold'],0)

    def test_failed_call_cost_is_part_of_total(self):
        rows = [
            {'truth': {'action': 'human'}, 'result': {'action': 'error'}, 'total_cost_usd': 0.25},
            {'truth': {'action': 'post', 'quantity': 12}, 'result': {'action': 'post', 'quantity': 12}, 'total_cost_usd': 0.5},
        ]
        result = summarize(rows)
        self.assertEqual(result['total_cost_usd'], 0.75)
        self.assertEqual(result['measured_cost_cases'], 2)
        self.assertEqual(result['technical_failures'], 1)
        del rows[0]['total_cost_usd']
        self.assertIsNone(summarize(rows)['total_cost_usd'])

    def test_invalid_cost_does_not_claim_complete_billing(self):
        for value in (True, -1, float('nan'), float('inf')):
            with self.subTest(value=value):
                result = summarize([{'truth': {'action': 'human'}, 'result': {'action': 'human'}, 'total_cost_usd': value}])
                self.assertIsNone(result['total_cost_usd'])
