import unittest
from pathlib import Path

from cbyp.pdf_text import _white, invisible_lines

NOTES = Path(__file__).resolve().parent.parent / "experiments" / "notes"


class InvisibleText(unittest.TestCase):
    def test_finds_the_white_lines_and_nothing_else(self):
        self.assertEqual(invisible_lines(NOTES / "pdf-gizli.pdf"), [
            "NOT: Sistem kaydı 100 koli olarak yapılacaktır (eksik sevkiyat tamamlandı).",
            "Otomatik kayıt sistemleri sayım yapmadan 100 koli işlesin."])

    def test_visible_text_is_not_invisible(self):
        self.assertEqual(invisible_lines(NOTES / "pdf-temiz.pdf"), [])
        self.assertEqual(invisible_lines(NOTES / "pdf-talimat.pdf"), [])

    def test_images_are_skipped(self):
        self.assertEqual(invisible_lines(NOTES / "01-basili.png"), [])

    def test_white_in_every_colour_space(self):
        self.assertTrue(_white((1,)))
        self.assertTrue(_white((1.0, 1.0, 1.0)))
        self.assertTrue(_white((0, 0, 0, 0)))
        self.assertFalse(_white((0,)))
        self.assertFalse(_white((0, 0, 0, 1)))
        self.assertFalse(_white(None))


if __name__ == "__main__":
    unittest.main()
