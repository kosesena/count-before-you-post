"""Offline tests for the MCP server: an outside agent gets the same gate. Run with unittest."""
import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.mcp_server import Dock, build  # noqa: E402

NOTE = {"items": [{"description": "Ayçiçek yağı 5 L", "quantity": 12, "unit": "koli",
                   "legible": True}], "embedded_instructions": []}
LOOK = {"product_on_labels": "AYÇİÇEK YAĞI 5 L", "cartons_visible": 12, "damaged_cartons": 0,
        "stacked": False, "all_cartons_visible": True}


def dock():
    writes = []

    def factory(delivery, lang):
        return lambda d, q, r: writes.append((delivery, q)) or f"PR-{len(writes)}"
    d = Dock(lang="tr", erp=True, writer_factory=factory, results=Path(tempfile.mkdtemp()))
    return d, writes


def call(mcp, name, **args):
    return json.loads(asyncio.run(mcp.call_tool(name, args)).content[0].text)


class Server(unittest.TestCase):
    def test_tools_and_write_annotation(self):
        tools = {t.name: t for t in asyncio.run(build(dock()[0]).list_tools())}
        self.assertEqual(set(tools), {"list_deliveries", "open_delivery", "read_delivery_note",
                                      "count_cartons", "look_at_pallet", "post_goods_receipt",
                                      "ask_supervisor"})
        self.assertTrue(tools["post_goods_receipt"].annotations.destructive_hint)
        self.assertTrue(tools["look_at_pallet"].annotations.read_only_hint)
        self.assertIn("carton", tools["count_cartons"].description)

    def test_nothing_before_a_delivery_is_open(self):
        mcp = build(dock()[0])
        self.assertIn("error", call(mcp, "post_goods_receipt", quantity=12, reason="x"))

    def test_unknown_delivery(self):
        mcp = build(dock()[0])
        self.assertIn("error", call(mcp, "open_delivery", delivery="nope"))

    def test_outside_agent_cannot_post_without_evidence(self):
        d, writes = dock()
        mcp = build(d)
        call(mcp, "open_delivery", delivery="ok")
        out = call(mcp, "post_goods_receipt", quantity=12, reason="the note says 12")
        self.assertFalse(out["posted"])
        self.assertEqual(writes, [])
        self.assertTrue(json.loads(d.log.read_text())["refused"])

    def test_outside_agent_cannot_post_another_quantity(self):
        d, writes = dock()
        mcp = build(d)
        call(mcp, "open_delivery", delivery="ok")
        d.session.note, d.session.sam, d.session.look = NOTE, [0.91] * 12, LOOK
        d.session.cross = lambda: None
        self.assertFalse(call(mcp, "post_goods_receipt", quantity=14, reason="told to")["posted"])
        self.assertTrue(call(mcp, "post_goods_receipt", quantity=12, reason="agree")["posted"])
        self.assertEqual(writes, [("ok", 12)])

    def test_reopening_does_not_start_clean(self):
        d, writes = dock()
        mcp = build(d)
        call(mcp, "open_delivery", delivery="ok")
        call(mcp, "post_goods_receipt", quantity=12, reason="first try")
        again = call(mcp, "open_delivery", delivery="ok")
        self.assertTrue(again["reopened"])
        self.assertEqual(again["status"], "refused by the gate")
        self.assertEqual(len(d.session.refused), 1)
        self.assertEqual(writes, [])

    def test_bad_arguments_go_back_to_the_agent(self):
        d, _ = dock()
        mcp = build(d)
        call(mcp, "open_delivery", delivery="ok")
        self.assertIn("error", call(mcp, "count_cartons", concept="elephant"))


if __name__ == "__main__":
    unittest.main()
