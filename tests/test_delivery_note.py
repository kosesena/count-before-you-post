import tempfile
import unittest
from pathlib import Path

from cbyp.delivery_note import _note_part


class FakeFiles:
    def __init__(self):
        self.uploads = []

    def create(self, file, purpose, expires_after):
        self.uploads.append((Path(file.name).name, purpose, expires_after["seconds"]))
        return type("F", (), {"id": f"file-{len(self.uploads)}"})()


class FakeAPI:
    def __init__(self):
        self.files = FakeFiles()


class NotePartTest(unittest.TestCase):
    def test_pdf_and_photo_go_in_through_the_files_api(self):
        api = FakeAPI()
        with tempfile.TemporaryDirectory() as d:
            pdf, png = Path(d) / "irsaliye.pdf", Path(d) / "irsaliye.png"
            pdf.write_bytes(b"%PDF-1.4 test")
            png.write_bytes(b"png")
            self.assertEqual(_note_part(pdf, api), {"type": "file", "file": {"file_id": "file-1"}})
            self.assertEqual(_note_part(png, api), {"type": "file", "file": {"file_id": "file-2"}})
        self.assertEqual(api.files.uploads, [("irsaliye.pdf", "user_data", 86400),
                                             ("irsaliye.png", "user_data", 86400)])

    def test_the_same_note_is_uploaded_once(self):
        api = FakeAPI()
        with tempfile.TemporaryDirectory() as d:
            note = Path(d) / "irsaliye.png"
            note.write_bytes(b"png")
            first, again = _note_part(note, api), _note_part(note, api)
        self.assertEqual(first, again)
        self.assertEqual(len(api.files.uploads), 1)


if __name__ == "__main__":
    unittest.main()
