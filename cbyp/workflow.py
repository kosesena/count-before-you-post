"""New-input, fully checked receiving workflow. Dry run by default; no fake receipts."""
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from .agent import Session
from .second_reader import SPARK_OPEN, read_note as second_read
from .wonder import audit_note
from .voice import turns, understand_dialogue


def full_session(note, camera, order, spoken=None, writer=None, audio=None, language="Turkish"):
    return Session(Path(note), Path(camera), order=order, spoken=spoken,
                   full_checks=True, writer=writer,
                   receiver_loader=(lambda: understand_dialogue(turns(audio, languages=[language]))["receiver"]) if audio else None,
                   second_reader=lambda p: second_read(p, model=SPARK_OPEN)["claim"],
                   auditor=audit_note)


def verify(note, camera, audio, order, language="Turkish", progress=None):
    """Models read fresh files. No ERP writer is installed. Missing inputs fail before calls."""
    if not order or not order.get("supplier") or not order.get("product") or not order.get("number"):
        raise ValueError("A trusted order number, supplier and exact product are required.")
    if any(type(order.get(k)) is not int or order[k] < 0 for k in ("ordered", "received")):
        raise ValueError("Order quantities must be non-negative integers.")
    if order["received"] > order["ordered"]:
        raise ValueError("Received quantity exceeds the order.")
    for path in (note, camera, audio):
        if not path or not Path(path).is_file():
            raise ValueError("A note, camera image and receiver WAV are required.")
    started = time.perf_counter()
    timings = []

    def step(name, fn):
        if progress: progress(name)
        t = time.perf_counter()
        try:
            return fn()
        finally:
            timings.append({"step": name, "seconds": round(time.perf_counter()-t, 3)})

    s = full_session(note, camera, order)
    step("Read delivery note", s.read_delivery_note)
    step("Inspect camera", s.look_at_pallet)
    step("Segment cartons", lambda: s.count_cartons("cardboard box"))
    spoken_turns = step("Transcribe speaker turns", lambda: turns(audio, languages=[language]))
    speech = step("Identify receiver count", lambda: understand_dialogue(spoken_turns))
    s.spoken = speech["receiver"]
    qty = (s.note.get("items") or [{}])[0].get("quantity", 0)
    result = step("Cross-check objects and authorize", lambda: s.call(
        "post_goods_receipt", json.dumps({"quantity": qty, "reason": "New-input verification"})))
    return {"mode": "dry_run", "erp_written": False, "result": result,
            "decision": asdict(s.last_decision) if s.last_decision else None,
            "note": s.note, "camera": s.look, "receiver": s.spoken,
            "speaker_turns": spoken_turns, "speech_interpretation": speech, "second_opinions": s.opinions,
            "trace": s.trace, "timings": timings,
            "seconds": round(time.perf_counter()-started, 3),
            "total_cost_usd": None, "cost_status": "Not measured: provider-wide billing required; not agent-token cost.",
            "input_sha256": {k: hashlib.sha256(Path(p).read_bytes()).hexdigest()
                             for k, p in (("note", note), ("camera", camera), ("audio", audio))}}
