import base64
import tempfile
import unittest
from pathlib import Path

from cbyp.delivery_note import _note_part


class NotePartTest(unittest.TestCase):
    def test_pdf_goes_in_as_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "irsaliye.pdf"
            path.write_bytes(b"%PDF-1.4 test")
            part = _note_part(path)
        self.assertEqual(part["type"], "file")
        self.assertEqual(part["file"]["filename"], "irsaliye.pdf")
        head, data = part["file"]["file_data"].split(",", 1)
        self.assertEqual(head, "data:application/pdf;base64")
        self.assertEqual(base64.b64decode(data), b"%PDF-1.4 test")

    def test_image_goes_in_as_image_url(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "irsaliye.png"
            path.write_bytes(b"png")
            part = _note_part(path)
        self.assertEqual(part["type"], "image_url")
        self.assertTrue(part["image_url"]["url"].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
