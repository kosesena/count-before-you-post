import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from cbyp.agent import Session
from cbyp.crosscheck import CrossCheck
from cbyp.frame_completeness import inspect_frame
from cbyp.sam import Segment

def mask(obj,conf,left,top,right,bottom):
    return Segment(obj,conf,left,top,right,bottom,bytes([1])*((right-left)*(bottom-top)))

PRODUCT='苦参素葡萄糖注射液'
def note(product=PRODUCT):
    return {'supplier':'Fixture', 'items':[{'description':product,'quantity':1,'unit':'carton','legible':True}], 'embedded_instructions':[]}
AUDIT={'ok':True,'quantity':True,'product':True,'instructions':''}
class FrameAndOCR(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'camera.jpg';Image.new('RGB',(1000,800)).save(self.path)
    def ready(self, product=PRODUCT, second=None):
        self.writes=[]
        s=Session(Path('note.png'),self.path,full_checks=True,
           order={'number':'PO','supplier':'Fixture','product':PRODUCT,'unit':'carton','ordered':1,'received':0},
           writer=lambda *args:self.writes.append(args),note=note(product),sam=[.95],
           look={'product_on_labels':PRODUCT,'cartons_visible':1,'damaged_cartons':0,'packaging_condition':'intact','stacked':False,'all_cartons_visible':True},
           concept=[mask('1',.95,100,100,900,700)],spoken={'quantity':1,'unit':'carton','certain':True},
           second_reader=lambda p:note(second if second is not None else product),auditor=lambda p,n:AUDIT)
        s.cross=lambda:CrossCheck(agreed=[(0,(500,400))]);return s
    def test_boundary_overrides_confident_camera_and_ocr_mismatch(self):
        for product in [PRODUCT,'苫参素葡萄糖注射液']:
            s=self.ready(product);s.concept=[mask('1',.95,0,0,700,600)]
            self.assertFalse(s.post_goods_receipt(1,'try')['posted'])
            self.assertEqual((s.last_decision.action,s.last_decision.rule),('human','frame_boundary'))
            self.assertEqual(self.writes,[])
    def test_clear_frame_can_still_accept(self):
        s=self.ready();self.assertTrue(s.post_goods_receipt(1,'try')['posted']);self.assertEqual(len(self.writes),1)
    def test_conflicting_readers_do_not_reject_or_autocorrect(self):
        for typo in ['苫参素葡萄糖注射液','苔参素葡萄糖注射液']:
            s=self.ready(typo,PRODUCT)
            self.assertFalse(s.post_goods_receipt(1,'try')['posted'])
            self.assertEqual((s.last_decision.action,s.last_decision.rule),('human','readers_disagree'))
            self.assertEqual(s.note['items'][0]['description'],typo);self.assertEqual(self.writes,[])
    def test_confirmed_wrong_product_still_blocks(self):
        s=self.ready('Wrong product ZX-99')
        self.assertFalse(s.post_goods_receipt(1,'try')['posted']);self.assertEqual(s.last_decision.action,'block')
    def test_audit_disputing_mismatch_goes_to_human(self):
        s=self.ready('Wrong product ZX-99');s.auditor=lambda *a:dict(AUDIT,ok=False,product=False)
        self.assertFalse(s.post_goods_receipt(1,'try')['posted']);self.assertEqual(s.last_decision.action,'human')
    def test_second_reader_failure_is_human_not_acceptance(self):
        s=self.ready('Wrong product ZX-99');s.second_reader=lambda p:1/0
        self.assertFalse(s.post_goods_receipt(1,'try')['posted']);self.assertEqual(s.last_decision.action,'human')
    def test_edges_and_low_confidence(self):
        for bounds in [(0,100,900,700),(100,0,900,700),(100,100,1000,700),(100,100,900,800)]:
            self.assertTrue(inspect_frame(self.path,[mask('a',.95,*bounds)])['requires_review'])
        self.assertFalse(inspect_frame(self.path,[Segment('noise',.2,0,0,1000,800,b'')])['requires_review'])
    def test_empty_bbox_padding_does_not_imply_mask_touches_edge(self):
        im=Image.new('L',(1000,800));im.paste(1,(100,100,900,700))
        segment=Segment('padded',.95,0,0,1000,800,im.tobytes())
        frame=inspect_frame(self.path,[segment])
        self.assertFalse(frame['requires_review'])
        self.assertEqual(frame['bbox_padding_only'][0]['occupied_bounds'],[100,100,900,700])

    def test_small_doubtful_edge_mask_still_requires_review(self):
        frame=inspect_frame(self.path,[mask('small',.71,0,400,3,403)])
        self.assertTrue(frame['requires_review'])
        self.assertEqual(frame['boundary_objects'][0]['confidence_band'],'doubtful')

    def test_one_occupied_edge_pixel_is_not_erased(self):
        im=Image.new('L',(1000,800));im.paste(1,(100,100,900,700));im.putpixel((0,400),1)
        self.assertTrue(inspect_frame(self.path,[Segment('edge',.95,0,0,1000,800,im.tobytes())])['requires_review'])

    def test_empty_truncated_or_outside_mask_fails_closed(self):
        for seg in [Segment('empty',.95,100,100,110,110,bytes(100)),
                    Segment('truncated',.95,100,100,110,110,b'1'),
                    mask('outside',.95,-1,10,20,30)]:
            with self.subTest(obj=seg.obj):
                with self.assertRaises(ValueError):inspect_frame(self.path,[seg])
                session=self.ready();session.concept=[seg]
                self.assertFalse(session.post_goods_receipt(1,'try')['posted'])
                self.assertEqual(session.last_decision.action,'human')
                self.assertEqual(self.writes,[])

    def test_input_read_failure_stops_write(self):
        s=self.ready();s.camera_path=Path('missing-camera.jpg')
        self.assertFalse(s.post_goods_receipt(1,'try')['posted']);self.assertEqual(s.last_decision.action,'human')
    def test_signoff_cannot_bypass_failed_required_checks(self):
        for failure in ['reader', 'audit', 'frame']:
            with self.subTest(failure=failure):
                s=self.ready()
                s.signoff={'approve':True,'quantity':1,'notes':'Previously approved'}
                if failure == 'reader':
                    s.second_reader=lambda p:1/0
                elif failure == 'audit':
                    s.auditor=lambda *args:1/0
                else:
                    s.camera_path=Path('missing-camera.jpg')
                result=s.post_goods_receipt(1,'try')
                self.assertFalse(result['posted'])
                self.assertEqual(result['gate'],'human')
                self.assertEqual(self.writes,[])
