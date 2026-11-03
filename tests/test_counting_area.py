import tempfile, unittest, hashlib
from pathlib import Path
from PIL import Image
from cbyp.counting_area import select_area, attach_area

class CountingAreaTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'source.jpg'
        im=Image.new('RGB',(200,100),'red');im.paste('blue',(100,0,200,100));im.save(self.path)
    def test_original_retained_and_pixels_match(self):
        original=self.path.read_bytes()
        crop,meta=select_area(self.path,{'box':[100,0,200,100],'confirmed':True},self.tmp.name)
        with Image.open(crop) as image: self.assertEqual(image.size,(100,100))
        self.assertEqual(self.path.read_bytes(),original)
        self.assertEqual(meta['original']['sha256'],hashlib.sha256(original).hexdigest())
        self.assertEqual(meta['analyzed']['sha256'],hashlib.sha256(crop.read_bytes()).hexdigest())
        self.assertIn('counting_area',attach_area({},meta))
    def test_invalid_or_unconfirmed_selection_rejected(self):
        for box in [[-1,0,100,100],[0,0,201,100],[100,0,20,100],[0,0,10,10],[0,0,100.1,100],[False,0,100,100]]:
            with self.subTest(box=box),self.assertRaises(ValueError):select_area(self.path,{'box':box,'confirmed':True},self.tmp.name)
        with self.assertRaises(ValueError):select_area(self.path,{'box':[0,0,100,100]},self.tmp.name)
    def test_exif_orientation_defines_coordinates(self):
        with Image.open(self.path) as original:
            im=original.copy();exif=original.getexif()
        exif[274]=6;im.save(self.path,exif=exif)
        crop,meta=select_area(self.path,{'box':[0,100,100,200],'confirmed':True},self.tmp.name)
        self.assertEqual(meta['original_size'],[100,200])
        with Image.open(crop) as image: self.assertEqual(image.size,(100,100))
    def test_default_unchanged(self):
        self.assertEqual(select_area(self.path,None,self.tmp.name),(self.path,None))

    def test_hosted_process_uses_crop_and_attaches_original(self):
        from unittest.mock import patch
        from api.verify import process
        payload={'consent':True,'language':'English','order':{},'note':{},'camera':{},'audio':{},'counting_area':{'box':[100,0,200,100],'confirmed':True}}
        def runner(note,camera,audio,order,language):
            with Image.open(camera) as image:self.assertEqual(image.size,(100,100))
            self.assertNotEqual(camera,self.path)
            return {'erp_written':False}
        with patch('cbyp.verify_server.decode_file',return_value=self.path):
            result=process(payload,runner=runner)
        self.assertEqual(result['counting_area']['original']['sha256'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertFalse(result['erp_written'])
