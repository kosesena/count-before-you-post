"""How much should the receiving agent reason? The same Spark agent on the six dock cases at
several reasoning efforts, without the gate, so what is measured is the agent itself.

Usage: CBYP_LANG=en .venv/bin/python experiments/effort_sweep.py [--out DIR] [effort ...] [-- variant ...]
No gate, so nothing is written to the ERP. Only the agent's own reasoning effort changes; the
tools it calls (Spark reading the note and looking at the pallet, SAM counting) keep theirs.
Appends one row per run to experiments/results/<lang>/effort_sweep.json; the Fireworks
workshop (30 Oct) suggested measuring this instead of assuming that more reasoning is better.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cbyp.agent as agent  # noqa: E402
from cbyp.agent import Session  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import OUT, RES  # noqa: E402

EFFORTS = ("minimal", "low", "medium", "high", "max")
RESULTS = RES / "effort_sweep.json"


class CountingAPI:
    """The agent's client, counting the tokens of its own responses."""

    def __init__(self, api):
        self.api, self.usage = api, {"input": 0, "output": 0, "reasoning": 0, "calls": 0}
        self.responses = self

    def create(self, **kw):
        resp = self.api.responses.create(**kw)
        u = getattr(resp, "usage", None)
        if u:
            self.usage["calls"] += 1
            self.usage["input"] += getattr(u, "input_tokens", 0) or 0
            self.usage["output"] += getattr(u, "output_tokens", 0) or 0
            d = getattr(u, "output_tokens_details", None)
            self.usage["reasoning"] += getattr(d, "reasoning_tokens", 0) or 0
        return resp


def one(out, truth, variant, effort):
    s = Session(out / f"depo-{variant}-irsaliye.png", out / f"depo-{variant}-kamera.png",
                gate=False, writer=None)
    api = CountingAPI(agent.client())
    start = time.perf_counter()
    try:
        # run() reads the module's REASONING on each call; pass it per run instead.
        answer = run_with_effort(s, api, effort)
        error = None
    except Exception as e:
        answer, error = None, str(e)[:300]
    expected = truth[variant]["expected_decision"]
    posted = [q for q, _ in s.posted]
    return {"variant": variant, "effort": effort, "expected": expected, "posted": posted,
            "supervisor": bool(s.escalated),
            "right": (bool(posted) == (expected == "post")) and not error,
            "tools": [t["tool"] for t in s.trace if "tool" in t],
            "thinking": sum("thinking" in t for t in s.trace),
            "usage": api.usage, "seconds": round(time.perf_counter() - start, 1),
            "answer": answer, "error": error, "trace": s.trace}


def run_with_effort(session, api, effort):
    reasoning = {"effort": effort, "summary": "auto"}
    resp = api.responses.create(model=agent.SPARK, instructions=agent.INSTRUCTIONS,
                                tools=agent.TOOLS, reasoning=reasoning, max_output_tokens=16000,
                                input="A delivery is waiting at the dock.")
    for _ in range(12):
        for t in agent._thoughts(resp):
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
        resp = api.responses.create(model=agent.SPARK, instructions=agent.INSTRUCTIONS,
                                    tools=agent.TOOLS, reasoning=reasoning,
                                    max_output_tokens=16000, previous_response_id=resp.id,
                                    input=outputs)
    return "(stopped: too many steps)"


def main(args):
    out = OUT
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    variants = args[args.index("--") + 1:] if "--" in args else []
    efforts = [a for a in (args[:args.index("--")] if "--" in args else args)] or list(EFFORTS)
    truth = json.loads((out / "depo-truth.json").read_text())
    jobs = [(v, e) for e in efforts for v in (variants or list(truth))]
    rows = json.loads(RESULTS.read_text()) if RESULTS.exists() else []
    # One worker per case: the six cases run side by side, the efforts one after another.
    with ThreadPoolExecutor(max_workers=6) as pool:
        for row in pool.map(lambda j: one(out, truth, *j), jobs):
            rows.append(row)
            RESULTS.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
            u = row["usage"]
            print(f"{row['effort']:8} {row['variant']:9} right={row['right']!s:5} "
                  f"posted={row['posted']} supervisor={row['supervisor']} "
                  f"tools={len(row['tools'])} out_tokens={u['output']} "
                  f"reasoning={u['reasoning']} {row['seconds']}s"
                  + (f" ERROR {row['error']}" if row["error"] else ""), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
