"""Where the dock scenes and results for one language live.

CBYP_LANG=tr (default) keeps the original paths; en, de and zh get their own subfolders,
so every language is measured the same way and none overwrites another.
"""
import os
from pathlib import Path

HERE = Path(__file__).parent
LANG = os.environ.get("CBYP_LANG", "tr")
LANGS = ("tr", "en", "de", "zh")
assert LANG in LANGS, f"CBYP_LANG must be one of {LANGS}"


def out(lang=LANG):
    return HERE / "blender" / "out" / ("" if lang == "tr" else lang)


def results(lang=LANG):
    return HERE / "results" / ("" if lang == "tr" else lang)


OUT, RES = out(), results()
RAW = RES / "sam_raw"
RES.mkdir(parents=True, exist_ok=True)
