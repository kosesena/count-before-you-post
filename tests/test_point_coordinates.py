"""Invalid model coordinates cannot be silently clamped into valid evidence."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from cbyp.perception import point_cartons

class Coordinates(unittest.TestCase):
 def test_out_of_range_and_noninteger_coordinates_fail(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image.png';Image.new('RGB',(100,80)).save(p)
   for value in [-1,1001,True,2.5]:
    response=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({'points':[{'x':value,'y':500}]})))])
    with self.subTest(value=value),patch('cbyp.perception.client') as client:
     client.return_value.chat.completions.create.return_value=response
     with self.assertRaises(ValueError):point_cartons(p)
 def test_coordinates_use_actual_image_axes(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image.png';Image.new('RGB',(200,100)).save(p)
   response=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({'points':[{'x':250,'y':750},{'x':1000,'y':1000}]})))])
   with patch('cbyp.perception.client') as client:
    client.return_value.chat.completions.create.return_value=response
    self.assertEqual(point_cartons(p),[(50,75),(199,99)])
