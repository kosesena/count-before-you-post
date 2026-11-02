"""New-input, fully checked receiving workflow. Dry run by default; no fake receipts."""
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from .agent import Session
from .product_identity import valid as valid_identity
from .second_reader import SPARK_OPEN, read_note as second_read
from .wonder import audit_note
from .voice import turns, understand_dialogue


def full_session(note, camera, order, spoken=None, writer=None, audio=None, language="Turkish"):
    return Session(Path(note), Path(camera), order=order, spoken=spoken,
                   full_checks=True, writer=writer,
                   receiver_loader=(lambda: understand_dialogue(turns(audio, languages=[language]))["receiver"]) if audio else None,
                   second_reader=lambda p: second_read(p, model=SPARK_OPEN)["claim"],
                   auditor=audit_note)


class VerificationRun:
    """In-memory checkpoint for one immutable, dry-run input set."""
    def __init__(self, note, camera, audio, order, language="Turkish"):
        validate_inputs(note, camera, audio, order)
        self.paths = dict(note=Path(note), camera=Path(camera), audio=Path(audio))
        self.order = json.loads(json.dumps(order))
        self.language = language
        self.hashes = self._hashes()
        self.session = full_session(note, camera, self.order)
        self.completed = {}
        self.timings = []
        self.failed_step = None

    def _hashes(self):
        return {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in self.paths.items()}

    @property
    def retryable(self):
        return self.failed_step in ("Transcribe speaker turns", "Identify receiver count")

    def run(self, progress=None):
        self.failed_step = None
        if self._hashes() != self.hashes:
            self.failed_step = None
            raise ValueError("Evidence changed; start a new verification.")
        self.failed_step = None
        def step(name, fn):
            if name in self.completed:
                return self.completed[name]
            if progress: progress(name)
            t = time.perf_counter()
            status = "error"
            try:
                value = fn()
                self.completed[name] = value
                status = "complete"
                return value
            except Exception:
                self.failed_step = name
                raise
            finally:
                self.timings.append({"step": name, "seconds": round(time.perf_counter()-t, 3), "status": status})

        s = self.session
        step("Read delivery note", s.read_delivery_note)
        step("Inspect camera", s.look_at_pallet)
        step("Segment cartons", lambda: s.count_cartons("cardboard box"))
        spoken_turns = step("Transcribe speaker turns", lambda: turns(self.paths['audio'], languages=[self.language]))
        speech = step("Identify receiver count", lambda: understand_dialogue(spoken_turns))
        s.spoken = speech["receiver"]
        qty = (s.note.get("items") or [{}])[0].get("quantity", 0)
        def authorize():
            result = s.call("post_goods_receipt", json.dumps({"quantity": qty, "reason": "New-input verification"}))
            if "error" in result:
                raise RuntimeError("Object authorization failed; no ERP write.")
            return result
        result = step("Cross-check objects and authorize", authorize)
        return {"mode": "dry_run", "erp_written": False, "result": result,
                "decision": asdict(s.last_decision) if s.last_decision else None,
                "note": s.note, "camera": s.look, "receiver": s.spoken,
                "speaker_turns": spoken_turns, "speech_interpretation": speech, "second_opinions": s.opinions,
                "trace": s.trace, "timings": self.timings,
                "seconds": round(sum(t['seconds'] for t in self.timings), 3),
                "total_cost_usd": None, "cost_status": "Not measured: provider-wide billing required; not agent-token cost.",
                "input_sha256": self.hashes}


def verify(note, camera, audio, order, language="Turkish", progress=None):
    """Models read fresh files. No ERP writer is installed."""
    validate_inputs(note, camera, audio, order)
    return VerificationRun(note, camera, audio, order, language).run(progress)


def validate_inputs(note, camera, audio, order):
    if order and "product_identity" in order and not valid_identity(order["product_identity"]):
        raise ValueError("Trusted identity requires brand and at least one product code or technical model; all fields must be strings.")
    if not order or not order.get("supplier") or not order.get("product") or not order.get("number"):
        raise ValueError("A trusted order number, supplier and exact product are required.")
    if any(type(order.get(k)) is not int or order[k] < 0 for k in ("ordered", "received")):
        raise ValueError("Order quantities must be non-negative integers.")
    if order["received"] > order["ordered"]:
        raise ValueError("Received quantity exceeds the order.")
    for path in (note, camera, audio):
        if not path or not Path(path).is_file():
            raise ValueError("A note, camera image and receiver WAV are required.")
