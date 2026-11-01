"""The gate as an MCP server, so an agent we did not write can work the dock.

Muse Code (or any MCP client) gets the same tools Spark gets in agent.py and the same gate:
the tool calls go through Session.call, so the outside agent cannot post a quantity the
evidence does not support, whatever the delivery note or the user tells it.

    {"mcp_servers": {"cbyp": {"transport": "stdio",
                              "command": "<repo>/.venv/bin/python",
                              "args": ["-m", "cbyp.mcp_server"],
                              "env": {"PYTHONPATH": "<repo>"}}}}

One server process = one MCP session. Opening a delivery again gives back the same one, with
what the gate already said: in the first Muse Code run (28 Oct 2026) the agent reopened a
blocked delivery five times to start clean, and each time the gate blocked it again.
Receipts go to the real ERPNext (CBYP_MCP_ERP=0: recorded, not written). Every tool call
lands in experiments/results/mcp/<time>-<delivery>.json. Logs go to stderr: stdout is the
MCP channel.
"""
import json
import os
import sys
import time
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from .agent import Session
from .gate import CONCEPTS
from .purchase_order import order_for

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("tr", "en", "de", "zh")
READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
# Muse connector classes: a tool that writes to the user's books is a "sensitive write".
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False,
                        openWorldHint=True)


def _scenes(lang):
    return ROOT / "experiments" / "blender" / "out" / ("" if lang == "tr" else lang)


def _erp_writer(delivery, lang):
    from .erpnext import Client
    erp = Client()
    ids = erp.ensure_master_data()
    ref = erp.ensure_order(order_for(lang), ids)

    def write(decision, quantity, reason):
        return erp.post_receipt(decision, supplier=ids["supplier"], item_code=ids["item_code"],
                                warehouse=ids["warehouse"],
                                note_number=f"MCP-{lang}-{delivery}", order_ref=ref)
    return write


class Dock:
    """The delivery the outside agent is working on, and where its trace is kept."""

    def __init__(self, lang=None, erp=None, writer_factory=_erp_writer, results=None):
        self.lang = lang or os.environ.get("CBYP_LANG", "tr")
        assert self.lang in LANGS, f"CBYP_LANG must be one of {LANGS}"
        self.erp = os.environ.get("CBYP_MCP_ERP", "1") != "0" if erp is None else erp
        self.writer_factory = writer_factory
        self.results = results or ROOT / "experiments" / "results" / "mcp"
        self.session = None
        self.delivery = None
        self.log = None
        self.opened = {}   # delivery -> (session, log): reopening never starts clean

    def deliveries(self):
        return sorted(p.name[len("depo-"):-len("-irsaliye.png")]
                      for p in _scenes(self.lang).glob("depo-*-irsaliye.png"))

    def open(self, delivery):
        if delivery not in self.deliveries():
            return {"error": f"no delivery {delivery!r}; choose one of {self.deliveries()}"}
        self.delivery = delivery
        if delivery in self.opened:
            self.session, self.log = self.opened[delivery]
            s = self.session
            status = ("posted" if s.posted else "with the supervisor" if s.escalated
                      else "refused by the gate" if s.refused else "at the dock")
            return {"delivery": delivery, "status": status, "reopened": True,
                    "posted": s.posted, "gate_refusals": [why for _, why in s.refused],
                    "note": "Same delivery, same evidence: the gate's answer will not change. "
                            "If it went to the supervisor, the supervisor decides."}
        out = _scenes(self.lang)
        writer = self.writer_factory(delivery, self.lang) if self.erp else None
        self.session = Session(out / f"depo-{delivery}-irsaliye.png",
                               out / f"depo-{delivery}-kamera.png", gate=True, writer=writer,
                               order=order_for(self.lang))
        self.log = self.results / f"{time.strftime('%Y%m%d-%H%M%S')}-{self.lang}-{delivery}.json"
        self.opened[delivery] = (self.session, self.log)
        return {"delivery": delivery, "status": "at the dock",
                "erp": "ERPNext" if self.erp else "dry run (nothing is written)"}

    def call(self, name, **args):
        if self.session is None:
            return {"error": "no delivery open: call open_delivery first"}
        result = self.session.call(name, json.dumps(args))
        s = self.session
        s.trace.append({"tool": name, "args": args, "result": result})
        self.results.mkdir(parents=True, exist_ok=True)
        self.log.write_text(json.dumps(
            {"client": "mcp", "lang": self.lang, "delivery": self.delivery,
             "posted": s.posted, "refused": s.refused, "escalated": s.escalated,
             "trace": s.trace}, ensure_ascii=False, indent=2, default=str))
        print(f"[cbyp] {self.delivery} {name} {args} -> {result}", file=sys.stderr, flush=True)
        return result


def build(dock=None):
    dock = dock or Dock()
    mcp = MCPServer("count-before-you-post", instructions=(
        "Goods receiving at a warehouse dock. Open a delivery, read its delivery note, count "
        "the cartons and look at the pallet, then post the goods receipt or ask the "
        "supervisor. The ERP write is behind a gate that checks the evidence your tools "
        "collected: it decides the quantity, not you."))

    @mcp.tool(annotations=READ)
    def list_deliveries() -> dict:
        """The deliveries waiting at the dock."""
        return {"deliveries": dock.deliveries(), "language": dock.lang}

    @mcp.tool(annotations=READ)
    def open_delivery(delivery: str) -> dict:
        """Start working on one delivery. Opening it again returns where it stands."""
        return dock.open(delivery)

    @mcp.tool(annotations=READ)
    def read_delivery_note() -> dict:
        """Read the delivery note with Muse Spark: supplier, items and quantities."""
        return dock.call("read_delivery_note")

    @mcp.tool(annotations=READ, description=(
        "Count the cartons on the pallet with SAM 3.1 on the ceiling camera. Returns sure and "
        "doubtful detections. SAM finds what the word names: if it finds nothing, try "
        "another word. Words: " + ", ".join(CONCEPTS)))
    def count_cartons(concept: str) -> dict:
        return dock.call("count_cartons", concept=concept)

    @mcp.tool(annotations=READ)
    def look_at_pallet() -> dict:
        """Muse Spark looks at the ceiling camera frame: product on the labels, carton count,
        damaged cartons, stacking."""
        return dock.call("look_at_pallet")

    @mcp.tool(annotations=WRITE)
    def post_goods_receipt(quantity: int, reason: str) -> dict:
        """Write the goods receipt to the ERP. The gate writes it only if the evidence agrees
        with this quantity; otherwise it refuses and says why."""
        return dock.call("post_goods_receipt", quantity=quantity, reason=reason)

    @mcp.tool(annotations=READ)
    def ask_supervisor(reason: str) -> dict:
        """Hand the delivery to the warehouse supervisor."""
        return dock.call("ask_supervisor", reason=reason)

    return mcp


if __name__ == "__main__":
    build().run("stdio")
