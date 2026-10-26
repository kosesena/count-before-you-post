# Count Before You Post

**An AI agent that can't write a number into an ERP until a camera has counted it.**

AI agents are getting write access to real systems, and they trust the document. Count Before You Post puts physical evidence between the agent and the ERP: Muse Spark reads the delivery note, SAM 3.1 counts what actually arrived, and a verification gate in code blocks the goods receipt in ERPNext when the two disagree, asking a human instead.

Built during the Meta Global AI Developer Hackathon (26 Oct – 4 Nov 2026). Everything in this repository was written during the event.

> Work in progress.

## The cast

![Spark, SAM, Kapı, Glimmer, Voice and the supervisor](assets/mascots/cast.jpg)

Spark (Muse Spark) reads the delivery note, SAM (SAM 3.1) counts what arrived, Kapı (the gate) compares them and decides whether the ERP may be written, Glimmer (Muse Glimmer) gives an independent second reading, Voice (Muse Voice Transcribe) listens to the receiver, and the supervisor approves when the gate is unsure.

*The characters are fan-made for this project with Muse Image. They are not official Meta mascots.*

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # add your META_API_KEY
```
