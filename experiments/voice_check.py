"""Muse Voice Transcribe on short Turkish receiving sentences, with and without keywords.

Usage: .venv/bin/python experiments/voice_check.py
Clips in experiments/voice/*.wav (macOS 'say -v Yelda', converted to 24 kHz mono WAV) with
truth.json; writes experiments/results/voice_check.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.voice import transcribe, understand  # noqa: E402

HERE = Path(__file__).parent
CLIPS = HERE / "voice"
KEYWORDS = ["koli", "Doğan Gıda", "ayçiçek yağı"]


def main():
    truth = json.loads((CLIPS / "truth.json").read_text())
    rows = []
    for name, t in truth.items():
        for kw in (None, KEYWORDS):
            text = transcribe(CLIPS / f"{name}.wav", keywords=kw)
            got = understand(text)
            ok = got["quantity"] == t["quantity"] and got["certain"] != t.get("uncertain", False)
            rows.append({"clip": name, "keywords": bool(kw), "transcript": text, **got,
                         "truth": t, "ok": ok})
            print(f"{'✓' if ok else '✗'} {name:14} kw={bool(kw)!s:5} {text!r} -> "
                  f"{got['quantity']} {got['supplier']!r} certain={got['certain']}")
    (HERE / "results" / "voice_check.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
