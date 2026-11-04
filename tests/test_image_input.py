"""All vision backends must receive the same oriented pixels and dimensions."""
import base64,io,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image,ImageOps
from cbyp.image_input import canonical_png
from cbyp.perception import look,point_cartons
from cbyp.sam import segment_image,segment_points

class ImageInput(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/'camera.jpg'
  image=Image.new('RGB',(120,80),'red');image.paste('blue',(0,0,30,40));exif=Image.Exif();exif[274]=6
  image.save(self.path,exif=exif)
 def test_all_exif_orientations_become_explicit_lossless_pixels(self):
  for orientation in range(1,9):
   with self.subTest(orientation=orientation):
    im=Image.new('RGB',(12,8),'red');im.putpixel((1,2),(0,0,255));exif=Image.Exif();exif[274]=orientation;im.save(self.path,exif=exif)
    before=self.path.read_bytes();data=canonical_png(self.path)
    with Image.open(self.path) as raw:expected=ImageOps.exif_transpose(raw).convert('RGB')
    actual=Image.open(io.BytesIO(data))
    self.assertEqual(actual.size,expected.size);self.assertEqual(actual.tobytes(),expected.tobytes())
    self.assertIsNone(actual.getexif().get(274));self.assertEqual(self.path.read_bytes(),before)
 def test_spark_and_sam_share_identical_payload_and_point_axes(self):
  with patch('cbyp.perception.client') as client:
   client.return_value.chat.completions.create.return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"points":[{"x":250,"y":750}]}'))])
   self.assertEqual(point_cartons(self.path),[(20,90)])
   point_url=client.return_value.chat.completions.create.call_args.kwargs['messages'][0]['content'][1]['image_url']['url']
   client.return_value.chat.completions.create.return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{}'))])
   look(self.path)
   look_url=client.return_value.chat.completions.create.call_args.kwargs['messages'][0]['content'][1]['image_url']['url']
  with patch('cbyp.sam.client') as client:
   client.return_value.responses.create.return_value=[]
   segment_image(self.path,'cardboard box')
   sam_url=client.return_value.responses.create.call_args.kwargs['input'][0]['content'][1]['image_url']
  self.assertEqual(point_url,look_url);self.assertEqual(point_url,sam_url)
  payload=Image.open(io.BytesIO(base64.b64decode(point_url.split(',',1)[1])))
  self.assertEqual(payload.size,(80,120));self.assertIsNone(payload.getexif().get(274))
  with patch('cbyp.sam.segment_image',return_value='') as segment:
   segment_points(self.path,[(20,90)])
   prompt=segment.call_args.args[1]
   self.assertIn('80',prompt);self.assertIn('120',prompt)

class LosslessTransport(unittest.TestCase):
 def test_webp_preserves_oriented_pixels_and_source_for_all_orientations(self):
  from cbyp.image_input import canonical_image
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'camera.jpg'
   for orientation in range(1,9):
    with self.subTest(orientation=orientation):
     image=Image.new('RGB',(120,80),'red');image.paste('blue',(0,0,30,40));exif=Image.Exif();exif[274]=orientation;image.save(path,exif=exif)
     original=path.read_bytes()
     with patch('cbyp.image_input.LOSSLESS_WEBP_THRESHOLD',0):mime,data=canonical_image(path)
     expected=Image.open(io.BytesIO(canonical_png(path)))
     actual=Image.open(io.BytesIO(data))
     self.assertEqual(mime,'image/webp')
     self.assertEqual(actual.size,expected.size)
     self.assertEqual(actual.convert('RGB').tobytes(),expected.convert('RGB').tobytes())
     self.assertIsNone(actual.getexif().get(274))
     self.assertEqual(path.read_bytes(),original)
