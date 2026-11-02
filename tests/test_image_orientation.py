"""Phone photo coordinates must match the EXIF-oriented media sent to the models."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PIL import Image
from cbyp.perception import point_cartons
from cbyp.sam import segment_points


class ImageOrientation(unittest.TestCase):
    def test_spark_points_and_sam_frame_use_display_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "phone.jpg"
            exif = Image.Exif()
            exif[274] = 6
            Image.new("RGB", (40, 20)).save(path, exif=exif)
            api = MagicMock()
            api.chat.completions.create.return_value = SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content='{"points":[{"x":250,"y":750}]}'))
            ])
            with patch("cbyp.perception.client", return_value=api):
                points = point_cartons(path)
            self.assertEqual(points, [(5, 30)])
            with patch("meta_sam_parser.build_object_prompt", return_value="prompt") as build:
                with patch("cbyp.sam.segment_image", return_value="result"):
                    self.assertEqual(segment_points(path, points), "result")
            self.assertEqual(build.call_args.kwargs['size'], (20, 40))


if __name__ == "__main__":
    unittest.main()
