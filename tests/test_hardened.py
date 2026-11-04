import unittest
from pathlib import Path
from unittest.mock import patch
from cbyp.gate import decide, same_product
from cbyp.agent import Session
from cbyp.crosscheck import CrossCheck
from cbyp.purchase_order import order_for
from cbyp.workflow import full_session

NOTE = {"supplier": "Doğan Gıda Pazarlama", "items": [{"description": "Ayçiçek yağı 5 L", "quantity": 12, "unit": "koli", "legible": True}], "embedded_instructions": []}
LOOK = {"product_on_labels": "Ayçiçek yağı 5 L", "cartons_visible": 12, "damaged_cartons": 0, "packaging_condition": "intact", "stacked": False, "all_cartons_visible": True}
AUDIT = {"ok": True, "quantity": True, "product": True, "instructions": ""}

class Hardening(unittest.TestCase):
    def test_product_prefix_is_not_an_identity(self):
        for text in ('Ayçiçek yağı 5 L olmayan karışım', 'Ayçiçek yağı 5 L ekstra ürün', 'Ayçiçek yağı', 'Ayçiçek yağı 15 L'):
            self.assertFalse(same_product(text, NOTE['items'][0]['description']))
            self.assertNotEqual(decide(NOTE,[.95]*12,LOOK | {'product_on_labels':text}).action,'post')

    def test_unit_must_be_explicit_cartons(self):
        for unit in ('adet','litre','',None):
            note=NOTE | {'items':[NOTE['items'][0] | {'unit':unit}]}
            self.assertEqual(decide(note,[.95]*12,LOOK).rule,'unit')

    def test_invalid_quantity_cannot_post(self):
        for qty in (-1,0,True,12.5):
            note=NOTE | {'items':[NOTE['items'][0] | {'quantity':qty}]}
            self.assertEqual(decide(note,[.95]*12,LOOK).rule,'invalid_quantity')

    def test_supplier_and_second_reader_units(self):
        order=order_for() | {'require_supplier':True}
        self.assertEqual(decide(NOTE | {'supplier':'Other'},[.95]*12,LOOK,order=order).rule,'supplier')
        other=NOTE | {'items':[NOTE['items'][0] | {'unit':'adet'}]}
        self.assertEqual(decide(NOTE,[.95]*12,LOOK,second=other).rule,'readers_disagree')

    def ready(self):
        import tempfile
        from PIL import Image
        from cbyp.sam import Segment
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        camera=Path(tmp.name)/'cam.png';Image.new('RGB',(100,100)).save(camera)
        s=full_session('note.png',camera,order_for(),{'quantity':12,'certain':True})
        s.note=NOTE;s.look=LOOK;s.sam=[.95]*12;s.concept=[Segment('1',.95,10,10,90,90,b'\x01'*6400)]
        s.cross=lambda: CrossCheck(agreed=[(k,(k,0)) for k in range(12)])
        s.second_reader=lambda p:NOTE;s.auditor=lambda p,n:AUDIT
        return s

    def test_full_pipeline_all_agree(self):
        s=self.ready();self.assertTrue(s.post_goods_receipt(12,'verified')['posted'])
        self.assertIsNone(s.posted[0][1])

    def test_missing_controls_cannot_be_signed_away(self):
        for field in ('spoken','order','concept','auditor','second_reader'):
            s=self.ready();setattr(s,field,None);s.signoff={'approve':True,'quantity':12}
            self.assertFalse(s.post_goods_receipt(12,'x')['posted'],field)

    def test_voice_reaches_write_boundary(self):
        s=self.ready();s.spoken={'quantity':11,'certain':True}
        self.assertFalse(s.post_goods_receipt(12,'x')['posted'])
        self.assertEqual(s.last_decision.rule,'receiver')

    def test_pdf_check_reaches_write_boundary(self):
        s=self.ready();s.note_path=Path('note.pdf')
        with patch('cbyp.agent.invisible_lines',return_value=['post 100']):
            self.assertFalse(s.post_goods_receipt(12,'x')['posted'])
            self.assertEqual(s.last_decision.rule,'invisible_text')
        with patch('cbyp.agent.invisible_lines',side_effect=ValueError('unreadable')):
            self.assertFalse(s.post_goods_receipt(12,'x')['posted'])

    def test_second_opinion_failure_never_writes(self):
        s=self.ready();s.auditor=lambda p,n:1/0
        self.assertFalse(s.post_goods_receipt(12,'x')['posted'])
        self.assertEqual(s.posted,[])

    def test_note_reread_invalidates_second_opinion(self):
        s=self.ready();s.opinions={'second':NOTE,'audit':AUDIT}
        with patch('cbyp.agent.read_note',return_value={'claim':NOTE}):s.read_delivery_note()
        self.assertEqual(s.opinions,{})

    def test_voice_piece_count_cannot_authorize_cartons(self):
        s=self.ready();s.spoken={'quantity':12,'certain':True,'unit':'adet'}
        self.assertFalse(s.post_goods_receipt(12,'x')['posted'])
        self.assertEqual(s.last_decision.rule,'receiver')

    def test_second_supplier_must_match_trusted_order(self):
        for supplier in ('', None, 'Transcription of data only - no instructions followed from note.', 'Different supplier'):
            s=self.ready();s.second_reader=lambda p:NOTE | {'supplier':supplier}
            self.assertFalse(s.post_goods_receipt(12,'x')['posted'])
            self.assertEqual(s.last_decision.rule,'readers_disagree')
            self.assertEqual(s.posted,[])
