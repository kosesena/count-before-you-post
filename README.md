# Count Before You Post

**An AI agent that can't write a number into an ERP until a camera has counted it.**

AI agents are getting write access to real systems, and they trust the document. Count Before You Post puts physical evidence between the agent and the ERP: Muse Spark reads the delivery note, SAM 3.1 counts what actually arrived, and a verification gate in code blocks the goods receipt in ERPNext when the two disagree, asking a human instead.

Built during the Meta Global AI Developer Hackathon (26 Oct – 4 Nov 2026). Everything in this repository was written during the event.

> Work in progress.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # add your META_API_KEY
```
