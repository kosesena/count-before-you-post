import unittest
from unittest.mock import patch
from cbyp.gate import decide
from test_gate import NOTE, SURE12, look
import test_hardened

class Packaging(unittest.TestCase):
    def test_condition_required(self):
        for condition in (None, '', True, 'uncertain', 'open_or_damaged'):
            camera=look() if condition is None else look(packaging_condition=condition)
            d=decide(NOTE,SURE12,camera,require_packaging=True)
            self.assertEqual((d.action,d.rule),('human','packaging'))
    def test_intact_positive_control(self):
        self.assertEqual(decide(NOTE,SURE12,look(packaging_condition='intact'),require_packaging=True).action,'post')
    def test_optional_legacy_still_honors_condition(self):
        self.assertEqual(decide(NOTE,SURE12,look(packaging_condition='open_or_damaged')).action,'human')
    def test_missing_condition_cannot_be_signed_away(self):
        helper=test_hardened.Hardening();s=helper.ready()
        try:
            s.look={k:v for k,v in s.look.items() if k!='packaging_condition'}
            s.signoff={'approve':True,'quantity':12}
            self.assertFalse(s.post_goods_receipt(12,'verified')['posted'])
            self.assertTrue(s.last_decision.evidence['required_check_failed'])
        finally:helper.doCleanups()
    def test_api_client_reuse_and_bounded_connect(self):
        from cbyp import meta
        with patch.dict(meta.os.environ,{'META_API_KEY':'test-only'}), patch.object(meta,'_clients',{}), patch.object(meta,'OpenAI') as factory:
            self.assertIs(meta.client(),meta.client())
            factory.assert_called_once()
            self.assertEqual(factory.call_args.kwargs['timeout'].connect,10)
            self.assertEqual(factory.call_args.kwargs['max_retries'],2)
