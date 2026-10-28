"""Speak the four receiving sentences in every language with ElevenLabs.

Usage: .venv/bin/python experiments/make_voice.py tr|en|de|zh
Needs ELEVENLABS_API_KEY in .env (optional ELEVENLABS_VOICE_ID; otherwise the first voice on
the account). Writes experiments/voice/<lang>/*.wav (Turkish: experiments/voice/*.wav, where
the dock reads it), 24 kHz mono 16-bit, and truth.json. The first Turkish clips, made with
macOS `say -v Yelda`, are kept in experiments/voice/tr-say/.
"""
import json
import os
import sys
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import _load_env  # noqa: E402

HERE = Path(__file__).parent
API = "https://api.elevenlabs.io/v1"

# Same four situations as the Turkish clips: plain, number last, self-correction, unsure.
SENTENCES = {
    "tr": {
        "01-basit": ("On iki koli geldi, Doğan Gıda'dan.", 12, "Doğan Gıda"),
        "02-sayi-sonda": ("Doğan Gıda'nın ayçiçek yağı geldi, toplam on bir koli.", 11,
                          "Doğan Gıda"),
        "03-duzeltme": ("Yirmi dört koli dedim ama yanlış saydım, aslında yirmi iki koli.", 22, ""),
        "04-belirsiz": ("Kolilerin bir kısmı üst üste, tam sayamadım, galiba on iki.", 12, ""),
    },
    "en": {
        "01-basit": ("Twelve cartons came in, from Harbor Foods.", 12, "Harbor Foods"),
        "02-sayi-sonda": ("Harbor Foods' sunflower oil is here, eleven cartons in total.", 11,
                          "Harbor Foods"),
        "03-duzeltme": ("I said twenty-four cartons, but I miscounted. It's actually twenty-two.",
                        22, ""),
        "04-belirsiz": ("Some of the cartons are stacked, I couldn't count them all. Twelve, I think.",
                        12, ""),
    },
    "de": {
        "01-basit": ("Zwölf Kartons sind angekommen, von Sonnenfeld Lebensmittel.", 12,
                     "Sonnenfeld Lebensmittel"),
        "02-sayi-sonda": ("Das Sonnenblumenöl von Sonnenfeld ist da, insgesamt elf Kartons.", 11,
                          "Sonnenfeld"),
        "03-duzeltme": ("Ich habe vierundzwanzig Kartons gesagt, aber ich habe mich verzählt. "
                        "Es sind eigentlich zweiundzwanzig.", 22, ""),
        "04-belirsiz": ("Ein Teil der Kartons ist gestapelt, ich konnte nicht alle zählen. "
                        "Ich glaube, zwölf.", 12, ""),
    },
    "zh": {
        "01-basit": ("到了十二箱，是海港食品送来的。", 12, "海港食品"),
        "02-sayi-sonda": ("海港食品的葵花籽油到了，一共十一箱。", 11, "海港食品"),
        "03-duzeltme": ("我刚才说二十四箱，但是数错了，其实是二十二箱。", 22, ""),
        "04-belirsiz": ("有些箱子摞在一起，我没数清楚，好像是十二箱。", 12, ""),
    },
}


def call(path, body=None):
    req = urllib.request.Request(
        API + path, data=json.dumps(body).encode() if body else None,
        method="POST" if body else "GET",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main(lang):
    _load_env()
    voice = os.environ.get("ELEVENLABS_VOICE_ID") or \
        json.loads(call("/voices"))["voices"][0]["voice_id"]
    out = HERE / "voice" / ("" if lang == "tr" else lang)
    out.mkdir(parents=True, exist_ok=True)
    truth = {}
    for name, (text, qty, supplier) in SENTENCES[lang].items():
        pcm = call(f"/text-to-speech/{voice}?output_format=pcm_24000",
                   {"text": text, "model_id": "eleven_multilingual_v2"})
        with wave.open(str(out / f"{name}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(pcm)
        truth[name] = {"quantity": qty, "supplier": supplier, "text": text}
        if name == "04-belirsiz":
            truth[name]["uncertain"] = True
        print(name, len(pcm) // 48000, "s")
    (out / "truth.json").write_text(json.dumps(truth, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
