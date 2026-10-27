# Muse Code task: ERPNext client

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
What it produced and what had to be fixed afterwards is recorded in `docs/JOURNAL.md`.

---

You are working in the repository `count-before-you-post`. Read `README.md`, `cbyp/gate.py`
and `tests/test_gate.py` first so the new code matches their style (short modules, plain
functions, a docstring at the top, comments only where the reason is not obvious).

## Goal

Write `cbyp/erpnext.py`: the only code in this project allowed to write to the ERP.
It writes a goods receipt (ERPNext doctype `Purchase Receipt`) through the ERPNext REST API,
and only when the gate allowed it.

## Requirements

1. Configuration from environment variables `ERPNEXT_URL`, `ERPNEXT_API_KEY`,
   `ERPNEXT_API_SECRET` (loaded the same way `cbyp/meta.py` loads `.env`; reuse its
   `_load_env`). Auth header: `Authorization: token <key>:<secret>`. Never print or log the
   key or secret.
2. Use only the Python standard library (`urllib.request`, `json`); no new dependencies.
   A `Client` class whose HTTP calls go through one method,
   `send(method, path, body=None) -> dict`, built on an injectable
   `transport(method, url, headers, body_bytes) -> (status, body_bytes)` function so tests
   can replace the network with a fake.
3. `ensure_master_data()`: idempotently create, if missing, a Supplier `Doğan Gıda`
   (supplier_group "All Supplier Groups"), an Item `AYC-5L` "Ayçiçek yağı 5 L"
   (stock item, UOM "Nos", item_group "All Item Groups") and use the existing company's
   `Stores - <abbr>` warehouse. Look up the company with the API, do not hard-code it.
4. `post_receipt(decision, *, supplier, item_code, warehouse, note_number)`:
   - `decision` is a `cbyp.gate.Decision`. If `decision.action != "post"`, raise
     `GateRefused` (a new exception) and make **no HTTP request at all**. This is the most
     important rule in the file.
   - Otherwise create a Purchase Receipt with one item (`qty` = `decision.quantity`,
     `received_qty` the same, `rate` 0 is fine), `supplier_delivery_note` = note_number,
     and put the gate's reasons into the `remarks` field. Then submit it
     (`docstatus` 1).
   - Return the created document name.
   - If ERPNext returns an error, raise an exception that includes ERPNext's message
     (`_server_messages` or `exception` field) but not the auth header.
5. Write `tests/test_erpnext.py` with `unittest` and a fake transport (no network):
   - a refused decision (block and human) makes zero requests and raises `GateRefused`,
   - a post decision sends the right JSON (supplier, item, qty, supplier_delivery_note,
     remarks) and submits,
   - an ERPNext error is raised with its message.
6. Run `.venv/bin/python -m unittest discover tests` and make every test pass, including
   the existing ones. Do not modify `cbyp/gate.py` or the existing tests.

Do not touch any other file. Do not commit. When done, list the files you created and the
test output.
