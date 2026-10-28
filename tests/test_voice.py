"""Offline tests for the voice turns parser. Run: .venv/bin/python -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.voice import parse_turns  # noqa: E402


class Turns(unittest.TestCase):
    def test_two_speakers(self):
        self.assertEqual(parse_turns("A:On iki koli getirdim.\nB:Saydım, on bir.\n"),
                         [{"speaker": "A", "transcript": "On iki koli getirdim."},
                          {"speaker": "B", "transcript": "Saydım, on bir."}])

    def test_wrapped_line_and_colon_in_text(self):
        got = parse_turns("A: Saat 10:30, on iki koli\ndevam ediyor\nB: tamam")
        self.assertEqual(got[0]["transcript"], "Saat 10:30, on iki koli devam ediyor")
        self.assertEqual(got[1], {"speaker": "B", "transcript": "tamam"})


if __name__ == "__main__":
    unittest.main()
