"""Muse Voice Transcribe on short Turkish receiving sentences, with and without keywords.

Usage: [CBYP_LANG=en|de|zh] .venv/bin/python experiments/voice_check.py
Turkish clips in experiments/voice/*.wav (macOS 'say -v Yelda', converted to 24 kHz mono WAV);
other languages in experiments/voice/<lang>/ (ElevenLabs, experiments/make_voice.py). Each
folder has a truth.json; writes voice_check.json to the language's results folder.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.voice import transcribe, understand  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import LANG, RES  # noqa: E402

CLIPS = HERE / "voice" / ("" if LANG == "tr" else LANG)
KEYWORDS = {"tr": ["koli", "Doğan Gıda", "ayçiçek yağı"],
            "en": ["cartons", "Harbor Foods", "sunflower oil"],
            "de": ["Kartons", "Sonnenfeld Lebensmittel", "Sonnenblumenöl"],
            "zh": ["箱", "海港食品", "葵花籽油"]}[LANG]
LANGUAGE = {"tr": "Turkish", "en": "English", "de": "German", "zh": "Chinese"}[LANG]


def main():
    truth = json.loads((CLIPS / "truth.json").read_text())
    rows = []
    for name, t in truth.items():
        for kw in (None, KEYWORDS):
            text = transcribe(CLIPS / f"{name}.wav", keywords=kw, languages=(LANGUAGE,))
            got = understand(text)
            ok = got["quantity"] == t["quantity"] and got["certain"] != t.get("uncertain", False)
            rows.append({"clip": name, "keywords": bool(kw), "transcript": text, **got,
                         "truth": t, "ok": ok})
            print(f"{'✓' if ok else '✗'} {name:14} kw={bool(kw)!s:5} {text!r} -> "
                  f"{got['quantity']} {got['supplier']!r} certain={got['certain']}")
    (RES / "voice_check.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
