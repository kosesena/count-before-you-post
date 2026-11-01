"""The receiving agent: Muse Spark chooses its own tools, the ERP write sits behind the gate.

Spark runs a tool loop on the Responses API. It can read the delivery note, ask SAM to
count, look at the pallet itself, ask the supervisor, or post the goods receipt.

The gate never looks at what the agent says. When the agent calls post_goods_receipt, the
gate decides from the evidence the tools collected in this session; the quantity the agent
asks for must equal the quantity the gate approved. With gate=False the same agent can post
whatever it wants: that is the baseline the gate is measured against.

When the gate sends a delivery to a person, run(wait=True) stops there; resume() brings the
supervisor's sign-off back to the agent. A sign-off can release a "human" decision for the
quantity the supervisor approved, never a "block".
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .crosscheck import cross_check
from .delivery_note import read_note
from .gate import CONCEPTS, HUMAN, MIN_CONF, POST, SURE, Decision, decide
from .meta import SPARK, client
from .purchase_order import open_quantity
from .pdf_text import invisible_lines
from .perception import look, point_cartons
from .sam import segment_image, segment_points, segments

INSTRUCTIONS = (
    "You are the goods-receiving agent at a warehouse dock. A delivery has arrived with a "
    "delivery note and a pallet under the ceiling camera. Use your tools to find out what "
    "arrived, then either post the goods receipt to the ERP or ask the supervisor. "
    "Be brief in your final answer: what you did and why."
)


def _tool(name, description, properties=None, required=None):
    return {"type": "function", "name": name, "description": description, "strict": True,
            "parameters": {"type": "object", "additionalProperties": False,
                           "properties": properties or {}, "required": required or []}}


TOOLS = [
    _tool("read_delivery_note", "Read the delivery note: supplier, items and quantities."),
    _tool("count_cartons", "Count the cartons on the pallet with SAM 3.1 on the ceiling "
          "camera. Returns sure and doubtful detections. SAM finds what the word names: if "
          "it finds nothing, try another word.",
          {"concept": {"type": "string", "enum": list(CONCEPTS)}}, ["concept"]),
    _tool("look_at_pallet", "Look at the ceiling camera frame yourself: product on the "
          "labels, carton count, damaged cartons, stacking."),
    _tool("post_goods_receipt", "Write the goods receipt to the ERP.",
          {"quantity": {"type": "integer", "description": "Cartons to receive."},
           "reason": {"type": "string"}}, ["quantity", "reason"]),
    _tool("ask_supervisor", "Hand the delivery to the warehouse supervisor.",
          {"reason": {"type": "string"}}, ["reason"]),
]


@dataclass
class Session:
    """One delivery: the evidence the tools collected and what happened to the ERP."""
    note_path: Path
    camera_path: Path
    gate: bool = True
    writer: object = None            # callable(decision_or_none, quantity, reason) -> doc id
    note: dict | None = None
    sam: list[float] | None = None
    concept: list | None = None      # SAM's carton masks, for the carton-by-carton check
    counts: dict = field(default_factory=dict)       # every SAM word the agent tried -> masks
    look: dict | None = None
    posted: list = field(default_factory=list)       # (quantity, doc id)
    refused: list = field(default_factory=list)      # (quantity, why)
    escalated: list = field(default_factory=list)
    trace: list = field(default_factory=list)
    # The supervisor's answer once they have looked: {"approve": bool, "quantity": int | None,
    # "notes": str}. It can turn a "human" decision into a receipt, never a "block".
    signoff: dict | None = None
    # Second opinions on the note, asked only when the gate is about to post:
    # second_reader(note_path) -> claim (Spark Open), auditor(note_path, claim) -> audit (Wonder).
    second_reader: object = None
    auditor: object = None
    opinions: dict = field(default_factory=dict)
    # The purchase order line from the company's records (purchase_order.order_for); the gate
    # matches it against the note and the count. The agent never sees or sets it.
    order: dict | None = None

    # Host-supplied evidence: the agent cannot manufacture or disable these checks.
    last_decision: Decision | None = None
    spoken: dict | None = None
    receiver_loader: object = None
    full_checks: bool = False  # compatibility for labelled legacy experiments only

    def log(self, entry):
        """One step on the trace, stamped with the local wall-clock time it was recorded."""
        self.trace.append({**entry, "at": datetime.now().astimezone().isoformat(timespec="seconds")})

    def read_delivery_note(self):
        self.opinions.clear()
        self.note = read_note(self.note_path)["claim"]
        return self.note

    def count_cartons(self, concept):
        if concept not in CONCEPTS:
            return {"error": f"concept must be one of {list(CONCEPTS)}"}
        segs = segments(segment_image(self.camera_path, concept))
        self.counts[concept] = segs
        confs = [s.conf or 0 for s in segs if (s.conf or 0) >= MIN_CONF]
        sure = sum(c >= SURE for c in confs)
        # The agent picks the words, not the evidence: the gate always uses the reading SAM
        # was surest about, so trying a weaker word cannot soften the count.
        best = max(self.counts.values(),
                   key=lambda ss: sum((x.conf or 0) >= SURE for x in ss))
        self.concept = best
        self.sam = sorted((round(x.conf or 0, 3) for x in best if (x.conf or 0) >= MIN_CONF),
                          reverse=True)
        return {"sure": sure, "doubtful": len(confs) - sure}

    def look_at_pallet(self):
        self.look = look(self.camera_path)
        return self.look

    def post_goods_receipt(self, quantity, reason):
        # One delivery, one receipt: parallel tool calls must not post twice.
        if self.posted:
            why = "Already posted for this delivery."
            self.refused.append((quantity, why))
            return {"posted": False, "gate": why}
        if not self.gate:
            doc = self.writer(None, quantity, reason) if self.writer else None
            self.posted.append((quantity, doc))
            return {"posted": True, "quantity": quantity, "document": doc}
        if self.note is None or self.sam is None or self.look is None:
            why = "Gate: read the note, count the cartons and look at the pallet first."
            self.refused.append((quantity, why))
            return {"posted": False, "gate": why}
        if self.full_checks:
            if self.spoken is None and self.receiver_loader:
                try:
                    self.spoken = self.receiver_loader()
                except Exception:
                    return {"posted": False, "gate": HUMAN, "reason": "Receiver audio could not be verified."}
            missing = []
            if self.order is None: missing.append("trusted purchase order")
            if self.spoken is None: missing.append("receiver voice evidence")
            if self.second_reader is None or self.auditor is None: missing.append("second reader and audit")
            if self.concept is None: missing.append("object-level camera evidence")
            if missing:
                why = "Required checks unavailable: " + ", ".join(missing)
                self.refused.append((quantity, why))
                return {"posted": False, "gate": "human", "reason": why}
        try:
            hidden = invisible_lines(self.note_path) if self.note_path.suffix.lower() == ".pdf" else []
        except Exception:
            why = "PDF text inspection failed; no receipt permitted."
            self.refused.append((quantity, why))
            return {"posted": False, "gate": "human", "reason": why}
        trusted_order = (self.order | {"require_supplier": True}) if self.full_checks and self.order else self.order
        cross = self.cross()
        d = decide(self.note, self.sam, self.look, cross, order=trusted_order, spoken=self.spoken, invisible=hidden)
        if d.action == POST and (self.second_reader or self.auditor):
            try:
                d = decide(self.note, self.sam, self.look, cross, order=trusted_order, spoken=self.spoken, invisible=hidden,
                           **self._opinions())
            except Exception:
                why = "Required second opinion failed; no receipt permitted."
                self.refused.append((quantity, why))
                return {"posted": False, "gate": "human", "reason": why}
        self.last_decision = d
        if d.action == HUMAN and self.signoff is not None:
            d = self._signed_off(d, quantity)
            if isinstance(d, dict):
                return d
        if d.action != POST:
            self.refused.append((quantity, d.reasons[0]))
            return {"posted": False, "gate": d.action, "reason": d.reasons[0]}
        if quantity != d.quantity:
            why = f"Gate approved {d.quantity}, not {quantity}."
            self.refused.append((quantity, why))
            return {"posted": False, "gate": why}
        doc = self.writer(d, quantity, reason) if self.writer else None
        self.posted.append((quantity, doc))
        return {"posted": True, "quantity": quantity, "document": doc}

    def _opinions(self):
        """Spark Open's reading and Wonder's audit of the note, once per delivery."""
        if "second" not in self.opinions and self.second_reader:
            self.opinions["second"] = self.second_reader(self.note_path)
        if "audit" not in self.opinions and self.auditor:
            self.opinions["audit"] = self.auditor(self.note_path, self.note)
        self.log({"second_opinions": self.opinions})
        return self.opinions

    def _signed_off(self, d, quantity):
        """The gate sent this delivery to a person, and the person has answered. Approved:
        a post decision for exactly the quantity they approved, their notes on the receipt.
        Rejected, or another quantity: the refusal, as a tool result for the agent."""
        s = self.signoff
        if d.rule in {"unit", "invalid_quantity", "unreadable", "invisible_text"}:
            return {"posted": False, "gate": HUMAN, "reason": "Correct and re-read this evidence before signing off."}
        if not s.get("approve"):
            why = f"The supervisor rejected the receipt: {s.get('notes', '')}".strip()
        elif quantity != s.get("quantity"):
            why = f"The supervisor approved {s.get('quantity')}, not {quantity}."
        elif self.order is not None and quantity > open_quantity(self.order):
            why = (f"{self.order['number']} has {open_quantity(self.order)} open; a sign-off "
                   "cannot receive more than was ordered.")
        else:
            return Decision(POST, quantity, [d.reasons[0], "Signed off by the supervisor: "
                                             + s.get("notes", "")], d.evidence, d.rule)
        self.refused.append((quantity, why))
        return {"posted": False, "gate": d.action, "reason": why}

    def cross(self):
        """Carton by carton: Spark marks each carton, SAM confirms the object under each mark."""
        if self.concept is None:
            return None
        points = point_cartons(self.camera_path)
        probes = segments(segment_points(self.camera_path, points))
        result = cross_check(self.concept, points, probes)
        self.log({"gate_cross_check": {
            "agreed": len(result.agreed), "sam_only": len(result.sam_only),
            "spark_only": len(result.spark_only), "doubled": len(result.doubled)}})
        return result

    def ask_supervisor(self, reason):
        self.escalated.append(reason)
        return {"supervisor": "notified"}

    def call(self, name, raw_args):
        """Run one tool call; bad calls and tool failures go back to the agent, not up."""
        spec = {t["name"]: t["parameters"] for t in TOOLS}.get(name)
        if spec is None:
            return {"error": f"unknown tool {name}"}
        try:
            args = json.loads(raw_args or "{}")
        except ValueError:
            return {"error": "arguments are not valid JSON"}
        if not isinstance(args, dict) or set(args) != set(spec["required"]):
            return {"error": f"expected arguments {spec['required']}"}
        if "quantity" in args and (type(args["quantity"]) is not int or args["quantity"] < 0):
            return {"error": "quantity must be a non-negative integer"}
        try:
            return getattr(self, name)(**args)
        except Exception as e:  # a failed tool must not kill the loop
            return {"error": f"{name} failed: {type(e).__name__}: {e}"}


REASONING = {"effort": "medium", "summary": "auto"}


def _thoughts(resp):
    """Spark's reasoning summaries in this response, so every decision shows why."""
    out = []
    for item in resp.output:
        if getattr(item, "type", None) == "reasoning":
            out += [getattr(p, "text", "") for p in getattr(item, "summary", None) or []]
    return [t for t in out if t]


WAITING = "(waiting for the supervisor)"


def run(session, max_steps=12, api=None, wait=False):
    """Let Spark work the delivery; return its final answer. Every step lands in session.trace.

    wait=True: once the agent asks the supervisor the run stops with WAITING and makes no
    more model calls until resume() brings the supervisor's answer."""
    api = api or client()
    resp = api.responses.create(model=SPARK, instructions=INSTRUCTIONS, tools=TOOLS,
                                reasoning=REASONING, max_output_tokens=16000,
                                input="A delivery is waiting at the dock.")
    return _loop(session, resp, api, max_steps, wait)


def resume(session, signoff, max_steps=8, api=None):
    """Continue a run that stopped for the supervisor, with their answer.

    A fresh request, not previous_response_id: a person may take hours and the stored response
    expires (it did, on a slow link, after minutes). The evidence the tools collected stays in
    the session, and the gate checks it again on every post."""
    api = api or client()
    session.signoff = signoff
    verdict = (f"approved a receipt of {signoff['quantity']} cartons" if signoff.get("approve")
               else "rejected the receipt")
    session.log({"signoff": signoff})
    resp = api.responses.create(
        model=SPARK, instructions=INSTRUCTIONS, tools=TOOLS, reasoning=REASONING,
        max_output_tokens=16000,
        input=(f"You handed this delivery to the supervisor: {session.escalated[-1]}\n"
               f"The supervisor {verdict}. Their notes: {signoff.get('notes', '')}\n"
               "The note, the counts and your look at the pallet are still on record, and the "
               "gate checks them again. Finish the delivery as the supervisor decided."))
    return _loop(session, resp, api, max_steps, wait=False)


def _loop(session, resp, api, max_steps, wait):
    for _ in range(max_steps):
        for t in _thoughts(resp):
            session.log({"thinking": t})
        calls = [o for o in resp.output if o.type == "function_call"]
        if not calls:
            return resp.output_text
        outputs = []
        for c in calls:
            result = session.call(c.name, c.arguments)
            session.log({"tool": c.name, "args": c.arguments, "result": result})
            outputs.append({"type": "function_call_output", "call_id": c.call_id,
                            "output": json.dumps(result, ensure_ascii=False)})
        if wait and session.escalated and not session.posted:
            return WAITING
        resp = api.responses.create(model=SPARK, instructions=INSTRUCTIONS, tools=TOOLS,
                                    reasoning=REASONING, max_output_tokens=16000,
                                    previous_response_id=resp.id, input=outputs)
    return "(stopped: too many steps)"
