"""Wonder drafts paperwork only when the gate refused, and the gate's rule picks the document."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.gate import BLOCK, HUMAN, POST, Decision  # noqa: E402
from cbyp.wonder import document_for, draft  # noqa: E402


class FakeLLM:
    def __init__(self):
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kw):
        self.calls.append(kw)
        content = ("TITLE: Teslimat itirazı\nTO: Tedarikçi\n\nSayın Yetkili, irsaliyede 12 "
                   "koli yazıyor, sayımda 11 koli bulundu. Bu bir taslaktır.")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class WonderTest(unittest.TestCase):
    def test_posted_receipt_needs_no_paperwork_and_no_call(self):
        llm = FakeLLM()
        self.assertIsNone(draft(Decision(POST, 12, ["ok"], rule="match"), {}, {}, llm=llm))
        self.assertEqual(llm.calls, [])

    def test_rule_picks_the_document(self):
        self.assertEqual(document_for(Decision(BLOCK, None, rule="wrong_product")), "supplier_dispute")
        self.assertEqual(document_for(Decision(BLOCK, 11, rule="mismatch")), "supplier_dispute")
        self.assertEqual(document_for(Decision(HUMAN, 11, rule="damaged")), "damage_report")
        self.assertEqual(document_for(Decision(BLOCK, None, rule="instruction")), "supervisor_note")
        self.assertEqual(document_for(Decision(HUMAN, None, rule="hidden")), "supervisor_note")

    def test_draft_uses_wonder_and_stays_a_draft(self):
        llm = FakeLLM()
        out = draft(Decision(BLOCK, 11, ["Counted 11, note says 12"], rule="mismatch"),
                    {"items": [{"quantity": 12}]}, {"sam_sure": 11}, language="Turkish", llm=llm)
        self.assertEqual(out["document"], "supplier_dispute")
        self.assertEqual(out["status"], "draft")
        self.assertEqual(out["title"], "Teslimat itirazı")
        self.assertEqual(out["to"], "Tedarikçi")
        call = llm.calls[0]
        self.assertEqual(call["model"], "muse-wonder-1.0")
        prompt = call["messages"][0]["content"]
        self.assertIn("in Turkish", prompt)
        self.assertIn("Counted 11, note says 12", prompt)


    def test_broken_form_is_rejected(self):
        from cbyp.wonder import parse
        self.assertIsNone(parse('function"}REDACTED? Need to reason more?"}'))
        self.assertIsNone(parse("TITLE: x\nTO: y\n\nshort"))

    def test_short_chinese_body_is_accepted(self):
        from cbyp.wonder import parse
        text = ("TITLE: 损坏报告\nTO: 供应商和承运人\n\n"
                "本次交付葵花籽油5升共12箱，其中1箱损坏。建议部分收货11箱。此为草稿，待主管批准。")
        self.assertEqual(parse(text)["title"], "损坏报告")


if __name__ == "__main__":
    unittest.main()
