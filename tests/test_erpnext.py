"""Offline tests for the ERPNext writer. Run: .venv/bin/python -m unittest discover tests"""
import json
import sys
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.erpnext import AlreadyReceived, Client, ERPNextError, GateRefused  # noqa: E402
from cbyp.gate import Decision  # noqa: E402


def client_for(fake):
    return Client(url="http://erp:8080", api_key="key", api_secret="s3cr3t",
                  transport=fake)


class Fake:
    """Stand-in for the network: canned replies, every call recorded."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, method, url, headers, body_bytes):
        self.calls.append({"method": method, "url": url, "headers": headers,
                           "body": json.loads(body_bytes.decode()) if body_bytes else None})
        status, payload = self.replies.pop(0)
        return status, json.dumps(payload).encode()


def ok(payload):
    return (200, payload)


POST = Decision("post", 12, ["Note, SAM and Spark agree on 12."])


def post(client, decision=POST):
    return client.post_receipt(decision, supplier="Doğan Gıda", item_code="AYC-5L",
                               warehouse="Stores - DG", note_number="IRS-42")


class Writer(unittest.TestCase):
    def test_block_and_human_make_no_requests(self):
        for action in ("block", "human"):
            fake = Fake([])
            with self.assertRaises(GateRefused):
                post(client_for(fake), Decision(action, 11, ["Counted 11, note says 12."]))
            self.assertEqual(fake.calls, [])

    def test_post_creates_and_submits(self):
        fake = Fake([ok({"data": []}), ok({"data": {"name": "MAT-PRE-0001"}}),
                     ok({"data": {"name": "MAT-PRE-0001", "docstatus": 1}})])
        self.assertEqual(post(client_for(fake)), "MAT-PRE-0001")
        self.assertEqual(len(fake.calls), 3)
        check, create, submit = fake.calls
        self.assertEqual(check["method"], "GET")
        self.assertIn("IRS-42", urllib.parse.unquote(check["url"]))
        self.assertEqual(create["method"], "POST")
        self.assertIn("Purchase", create["url"])
        item = create["body"]["items"][0]
        self.assertEqual((create["body"]["supplier"], item["item_code"],
                          item["qty"], item["received_qty"],
                          create["body"]["supplier_delivery_note"]),
                         ("Doğan Gıda", "AYC-5L", 12, 12, "IRS-42"))
        self.assertIn("agree on 12", create["body"]["remarks"])
        self.assertEqual((submit["method"], submit["body"]), ("PUT", {"docstatus": 1}))
        self.assertIn("MAT-PRE-0001", submit["url"])

    def test_a_delivery_already_received_is_not_written_again(self):
        fake = Fake([ok({"data": [{"name": "MAT-PRE-0001"}]})])
        with self.assertRaises(AlreadyReceived) as ctx:
            post(client_for(fake))
        self.assertIn("MAT-PRE-0001", str(ctx.exception))
        self.assertEqual([c["method"] for c in fake.calls], ["GET"])

    def test_server_error_carries_message_not_secret(self):
        server = {"exception": "ValidationError",
                  "_server_messages": json.dumps([json.dumps({"message": "Item AYC-5L is not a stock item"})])}
        fake = Fake([ok({"data": []}), (417, server)])
        with self.assertRaises(ERPNextError) as ctx:
            post(client_for(fake))
        self.assertIn("not a stock item", str(ctx.exception))
        self.assertNotIn("s3cr3t", str(ctx.exception))

    def test_ensure_master_data_creates_missing(self):
        missing = (404, {"exception": "DoesNotExistError"})
        fake = Fake([missing, ok({"data": {"name": "Doğan Gıda"}}),
                     ok({"data": {"name": "AYC-5L"}}),
                     ok({"data": [{"name": "Dogan AS", "abbr": "DG"}]}),
                     ok({"data": {"name": "Stores - DG"}})])
        ids = client_for(fake).ensure_master_data()
        self.assertEqual(ids, {"supplier": "Doğan Gıda", "item_code": "AYC-5L",
                               "warehouse": "Stores - DG"})
        made = fake.calls[1]
        self.assertEqual(made["method"], "POST")
        self.assertEqual(made["body"]["supplier_group"], "All Supplier Groups")
        self.assertTrue(all(c["method"] == "GET" for c in fake.calls[2:]))



class Orders(unittest.TestCase):
    ORDER = {"number": "PO-2026-1047", "ordered": 12, "received": 0}
    IDS = {"supplier": "Doğan Gıda", "item_code": "AYC-5L", "warehouse": "Stores - DG"}

    def test_existing_order_is_found_again_not_created(self):
        fake = Fake([ok({"data": [{"name": "PUR-ORD-1"}]}),
                     ok({"data": {"name": "PUR-ORD-1", "items": [{"name": "row-1"}]}})])
        ref = client_for(fake).ensure_order(self.ORDER, self.IDS)
        self.assertEqual(ref, {"purchase_order": "PUR-ORD-1", "purchase_order_item": "row-1"})
        self.assertEqual([c["method"] for c in fake.calls], ["GET", "GET"])
        self.assertIn("PO-2026-1047", urllib.parse.unquote(fake.calls[0]["url"]))

    def test_missing_order_is_created_and_submitted(self):
        fake = Fake([ok({"data": []}), ok({"data": {"name": "PUR-ORD-2"}}),
                     ok({"data": {"name": "PUR-ORD-2", "docstatus": 1}}),
                     ok({"data": {"name": "PUR-ORD-2", "items": [{"name": "row-2"}]}})])
        ref = client_for(fake).ensure_order(self.ORDER, self.IDS)
        self.assertEqual(ref["purchase_order"], "PUR-ORD-2")
        create, submit = fake.calls[1], fake.calls[2]
        self.assertEqual(create["body"]["order_confirmation_no"], "PO-2026-1047")
        self.assertEqual(create["body"]["items"][0]["qty"], 12)
        self.assertEqual(submit["body"], {"docstatus": 1})

    def test_receipt_line_is_tied_to_the_order_line(self):
        fake = Fake([ok({"data": []}), ok({"data": {"name": "MAT-PRE-0002"}}),
                     ok({"data": {"name": "MAT-PRE-0002", "docstatus": 1}})])
        client_for(fake).post_receipt(POST, supplier="Doğan Gıda", item_code="AYC-5L",
                                      warehouse="Stores - DG", note_number="IRS-43",
                                      order_ref={"purchase_order": "PUR-ORD-1",
                                                 "purchase_order_item": "row-1"})
        line = fake.calls[1]["body"]["items"][0]
        self.assertEqual((line["purchase_order"], line["purchase_order_item"]),
                         ("PUR-ORD-1", "row-1"))


if __name__ == "__main__":
    unittest.main()
