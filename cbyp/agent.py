"""The receiving agent: Muse Spark chooses its own tools, the ERP write sits behind the gate.

Spark runs a tool loop on the Responses API. It can read the delivery note, ask SAM to
count, look at the pallet itself, ask the supervisor, or post the goods receipt.

The gate never looks at what the agent says. When the agent calls post_goods_receipt, the
gate decides from the evidence the tools collected in this session; the quantity the agent
asks for must equal the quantity the gate approved. With gate=False the same agent can post
whatever it wants: that is the baseline the gate is measured against.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path

from .crosscheck import cross_check
from .delivery_note import read_note
from .gate import CONCEPTS, MIN_CONF, POST, SURE, decide
from .meta import SPARK, client
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

    def read_delivery_note(self):
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
        d = decide(self.note, self.sam, self.look, self.cross())
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

    def cross(self):
        """Carton by carton: Spark marks each carton, SAM confirms the object under each mark."""
        if self.concept is None:
            return None
        points = point_cartons(self.camera_path)
        probes = segments(segment_points(self.camera_path, points))
        result = cross_check(self.concept, points, probes)
        self.trace.append({"gate_cross_check": {
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


def run(session, max_steps=12, api=None):
    """Let Spark work the delivery; return its final answer. Every step lands in session.trace."""
    api = api or client()
    resp = api.responses.create(model=SPARK, instructions=INSTRUCTIONS, tools=TOOLS,
                                reasoning=REASONING, max_output_tokens=16000,
                                input="A delivery is waiting at the dock.")
    for _ in range(max_steps):
        for t in _thoughts(resp):
            session.trace.append({"thinking": t})
        calls = [o for o in resp.output if o.type == "function_call"]
        if not calls:
            return resp.output_text
        outputs = []
        for c in calls:
            result = session.call(c.name, c.arguments)
            session.trace.append({"tool": c.name, "args": c.arguments, "result": result})
            outputs.append({"type": "function_call_output", "call_id": c.call_id,
                            "output": json.dumps(result, ensure_ascii=False)})
        resp = api.responses.create(model=SPARK, instructions=INSTRUCTIONS, tools=TOOLS,
                                    reasoning=REASONING, max_output_tokens=16000,
                                    previous_response_id=resp.id, input=outputs)
    return "(stopped: too many steps)"
