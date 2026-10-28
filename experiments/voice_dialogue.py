"""Driver and receiver at the dock: does the receiver's count survive the driver's number?

Usage: .venv/bin/python experiments/voice_dialogue.py make   # ElevenLabs, two voices
       .venv/bin/python experiments/voice_dialogue.py check  # Muse Voice Transcribe + Spark
Clips in experiments/voice/dialogue/ (24 kHz mono 16-bit, 0.6 s between turns), truth.json
next to them. check reads every clip two ways and writes results/voice_dialogue.json:
  plain      PUSH_TO_TALK transcript -> voice.understand()   (one block of text, no speakers)
  diarized   DIARIZATION turns -> voice.understand_dialogue() (who said what)
"""
import json
import os
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import _load_env  # noqa: E402
from cbyp.voice import transcribe, turns, understand, understand_dialogue  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from make_voice import call  # noqa: E402

CLIPS = HERE / "voice" / "dialogue"
RES = HERE / "results"
KEYWORDS = ["koli", "Doğan Gıda", "ayçiçek yağı"]
D, R = "driver", "receiver"

# (speaker, sentence) turns; receiver = their own last count; driver = what they claim.
DIALOGUES = {
    "01-eksik": ([(D, "Doğan Gıda'dan on iki koli getirdim, imzalar mısınız?"),
                  (R, "Bir dakika, saydım, on bir koli var. Biri eksik.")],
                 {"receiver": 11, "driver": 12, "uncertain": False}),
    "02-tamam": ([(D, "On iki koli ayçiçek yağı, Doğan Gıda."),
                  (R, "Saydım, on iki. Tamam.")],
                 {"receiver": 12, "driver": 12, "uncertain": False}),
    "03-son-soz": ([(R, "Burada on koli var."),
                    (D, "Hayır, on iki getirdim, ikisi arkada kaldı."),
                    (R, "Arkaya da baktım, yok. On koli.")],
                   {"receiver": 10, "driver": 12, "uncertain": False}),
    "04-sofor-sonda": ([(R, "On bir koli saydım."),
                        (D, "Bende irsaliyede on iki yazıyor, on iki diye girin.")],
                       {"receiver": 11, "driver": 12, "uncertain": False}),
    "05-belirsiz": ([(D, "Yirmi koli getirdim."),
                     (R, "Üst üste duruyorlar, tam sayamadım, galiba on sekiz.")],
                    {"receiver": 18, "driver": 20, "uncertain": True}),
}


def make():
    _load_env()
    voices = [v["voice_id"] for v in json.loads(call("/voices"))["voices"]]
    who = {R: os.environ.get("ELEVENLABS_VOICE_ID") or voices[0]}
    who[D] = os.environ.get("ELEVENLABS_DRIVER_VOICE_ID") or next(v for v in voices
                                                                    if v != who[R])
    CLIPS.mkdir(parents=True, exist_ok=True)
    gap = b"\0\0" * int(24000 * 0.6)
    truth = {}
    for name, (lines, t) in DIALOGUES.items():
        pcm = gap.join(call(f"/text-to-speech/{who[s]}?output_format=pcm_24000",
                            {"text": text, "model_id": "eleven_multilingual_v2"})
                       for s, text in lines)
        with wave.open(str(CLIPS / f"{name}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(pcm)
        truth[name] = {**t, "lines": lines}
        print(name, len(pcm) // 48000, "s")
    (CLIPS / "truth.json").write_text(json.dumps(truth, ensure_ascii=False, indent=1))


def check():
    truth = json.loads((CLIPS / "truth.json").read_text())
    rows = []
    for name, t in truth.items():
        wav = CLIPS / f"{name}.wav"
        plain = understand(transcribe(wav, keywords=KEYWORDS))
        said = turns(wav, keywords=KEYWORDS)
        dia = understand_dialogue(said)
        for way, got in (("plain", plain), ("diarized", dia["receiver"])):
            ok = got["quantity"] == t["receiver"] and got["certain"] != t["uncertain"]
            rows.append({"clip": name, "way": way, "quantity": got["quantity"],
                         "certain": got["certain"], "truth": t["receiver"], "ok": ok,
                         **({"turns": said, "driver_quantity": dia["driver_quantity"],
                             "speakers": len({x["speaker"] for x in said})}
                            if way == "diarized" else {})})
            print(f"{'✓' if ok else '✗'} {name:15} {way:8} -> {got['quantity']} "
                  f"certain={got['certain']} (truth {t['receiver']})")
    for way in ("plain", "diarized"):
        r = [x for x in rows if x["way"] == way]
        print(f"{way}: {sum(x['ok'] for x in r)}/{len(r)}")
    (RES / "voice_dialogue.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    {"make": make, "check": check}[sys.argv[1]]()
