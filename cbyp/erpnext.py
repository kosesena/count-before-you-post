"""Write goods receipts to ERPNext, and only when the gate allowed it.

This module is the only code in the project allowed to write to the ERP.
Every HTTP call goes through Client.send; post_receipt refuses anything the
gate did not approve before any request is made.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .gate import Decision
from .meta import _load_env

SUPPLIER = "Doğan Gıda"
SUPPLIER_GROUP = "All Supplier Groups"
ITEM_CODE = "AYC-5L"
ITEM_NAME = "Ayçiçek yağı 5 L"
ITEM_GROUP = "All Item Groups"
UOM = "Nos"


class GateRefused(Exception):
    """The gate did not approve this receipt, so nothing was sent."""


class ERPNextError(Exception):
    """An ERPNext call failed; carries the server message, never the auth header."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def _quote(part):
    return urllib.parse.quote(part, safe="")


def _default_transport(method, url, headers, body_bytes):
    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _describe(method, path, status, payload, raw):
    found = []
    # _server_messages is a JSON list of JSON-encoded {"message": ...} dicts.
    msgs = payload.get("_server_messages") if isinstance(payload, dict) else None
    if isinstance(msgs, str):
        try:
            msgs = json.loads(msgs)
        except ValueError:
            msgs = []
    for entry in msgs or []:
        try:
            entry = json.loads(entry) if isinstance(entry, str) else entry
        except ValueError:
            pass
        text = entry.get("message", entry) if isinstance(entry, dict) else entry
        if text:
            found.append(str(text))
    exc = payload.get("exception") if isinstance(payload, dict) else None
    if exc:
        found.append(str(exc))
    if not found:
        try:
            found.append(raw.decode()[:500])
        except (UnicodeDecodeError, AttributeError):
            found.append(repr(raw)[:500])
    return f"ERPNext {method} {path} failed ({status}): {'; '.join(found)}"


def _refuse(decision):
    raise GateRefused(f"Gate action is '{decision.action}', not 'post': "
                      + ("; ".join(decision.reasons) or "no reason given"))


class Client:
    """ERPNext REST client. Auth lives in the header only, never in logs."""

    def __init__(self, url=None, api_key=None, api_secret=None, transport=None):
        _load_env()
        self.base = (url or os.environ.get("ERPNEXT_URL") or "").rstrip("/")
        self.api_key = api_key or os.environ.get("ERPNEXT_API_KEY")
        self.api_secret = api_secret or os.environ.get("ERPNEXT_API_SECRET")
        if not self.base or not self.api_key or not self.api_secret:
            raise RuntimeError("ERPNEXT_URL, ERPNEXT_API_KEY and ERPNEXT_API_SECRET must be set")
        self.transport = transport or _default_transport

    def send(self, method, path, body=None):
        """Do one JSON request; return the decoded response dict."""
        headers = {"Authorization": f"token {self.api_key}:{self.api_secret}",
                   "Accept": "application/json", "Content-Type": "application/json"}
        data = json.dumps(body).encode() if body is not None else None
        status, raw = self.transport(method, self.base + path, headers, data)
        try:
            payload = json.loads(raw.decode()) if raw else {}
        except ValueError:
            payload = {}
        if status >= 400:
            raise ERPNextError(_describe(method, path, status, payload, raw), status)
        return payload

    def _get_or_create(self, doctype, name, make):
        try:
            self.send("GET", f"/api/resource/{_quote(doctype)}/{_quote(name)}")
        except ERPNextError as e:
            if e.status != 404:
                raise
            self.send("POST", f"/api/resource/{_quote(doctype)}", make)

    def ensure_master_data(self):
        """Create supplier/item when missing; return ids incl. company warehouse."""
        self._get_or_create("Supplier", SUPPLIER,
                            {"supplier_name": SUPPLIER, "supplier_group": SUPPLIER_GROUP})
        self._get_or_create("Item", ITEM_CODE,
                            {"item_code": ITEM_CODE, "item_name": ITEM_NAME,
                             "item_group": ITEM_GROUP, "stock_uom": UOM, "is_stock_item": 1})
        # The company is looked up, never hard-coded; its main store follows ERPNext naming.
        companies = self.send("GET", "/api/resource/Company?limit_page_length=1&fields="
                              + _quote('["name","abbr"]'))
        rows = companies.get("data") or []
        if not rows:
            raise ERPNextError("No Company found in ERPNext")
        warehouse = f"Stores - {rows[0]['abbr']}"
        self.send("GET", f"/api/resource/Warehouse/{_quote(warehouse)}")
        return {"supplier": SUPPLIER, "item_code": ITEM_CODE, "warehouse": warehouse}

    def post_receipt(self, decision, *, supplier, item_code, warehouse, note_number):
        """Create and submit a Purchase Receipt; refuse anything but a post decision."""
        if decision.action != "post":
            _refuse(decision)
        if decision.quantity is None:
            raise ValueError("Post decision carries no quantity.")
        doc = {"supplier": supplier, "supplier_delivery_note": note_number,
               "remarks": "\n".join(decision.reasons),
               "items": [{"item_code": item_code, "qty": decision.quantity,
                          "received_qty": decision.quantity, "rate": 0,
                          "warehouse": warehouse}]}
        created = self.send("POST", f"/api/resource/{_quote('Purchase Receipt')}", doc)
        name = (created.get("data") or {}).get("name")
        if not name:
            raise ERPNextError("ERPNext did not return a document name.")
        self.send("PUT", f"/api/resource/{_quote('Purchase Receipt')}/{_quote(name)}",
                  {"docstatus": 1})
        return name


def ensure_master_data(client=None):
    """Module-level wrapper; uses a default client built from the environment."""
    return (client or Client()).ensure_master_data()


def post_receipt(decision, *, supplier, item_code, warehouse, note_number, client=None):
    """Module-level wrapper; the gate check runs before any client or request exists."""
    if decision.action != "post":
        _refuse(decision)
    return (client or Client()).post_receipt(
        decision, supplier=supplier, item_code=item_code,
        warehouse=warehouse, note_number=note_number)
