"""The agent stops for the supervisor, the supervisor signs off, the agent finishes.

Usage: .venv/bin/python experiments/run_signoff.py [variant ...]
For the two dock cases the gate sends to a person: the agent runs with wait=True and stops at
ask_supervisor; a scripted supervisor answer (below) goes back through resume(); the gate
checks the evidence again and only the quantity the supervisor approved can be written, to
the real ERPNext. Writes experiments/results/signoff.json after every step.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbyp.agent import WAITING, Session, resume, run  # noqa: E402
from paths import LANG, OUT, RES  # noqa: E402
from run_agent import erp_writer  # noqa: E402

RESULTS = RES / "signoff.json"
# What Şef says after walking over to the pallet.
SIGNOFF = {
    "hasarli": {"approve": True, "quantity": 11,
                "notes": "The crushed carton goes to quarantine; receive the 11 intact ones."},
    "belirsiz": {"approve": True, "quantity": 12,
                 "notes": "Unstacked the load and counted by hand: 12 intact cartons."},
}


def save(rows):
    RESULTS.write_text(json.dumps(rows, ensure_ascii=False, indent=2))


def main(variants):
    rows = json.loads(RESULTS.read_text()) if RESULTS.exists() else []
    for v in variants or list(SIGNOFF):
        writer = erp_writer(f"signoff-{v}")
        for attempt in range(3):
            s = Session(OUT / f"depo-{v}-irsaliye.png", OUT / f"depo-{v}-kamera.png",
                        writer=writer)
            try:
                first = run(s, wait=True)
                break
            except Exception as e:
                print(f"{v}: attempt {attempt + 1} failed before sign-off: {e}", flush=True)
                if s.posted or attempt == 2:
                    raise
        row = {"variant": v, "lang": LANG, "first_answer": first, "escalated": s.escalated,
               "posted_before_signoff": list(s.posted), "signoff": SIGNOFF[v]}
        rows.append(row)
        save(rows)
        print(f"{v:9} first={first!r} escalated={len(s.escalated)} posted={s.posted}", flush=True)
        if first != WAITING:
            continue
        start = time.perf_counter()
        try:
            row["answer"] = resume(s, SIGNOFF[v])
        except Exception as e:  # saved as it is: a written receipt must never be lost
            row["error"] = f"{type(e).__name__}: {e}"
        row.update({"posted": s.posted, "refused": s.refused,
                    "tools": [t["tool"] for t in s.trace if "tool" in t],
                    "seconds_after_signoff": round(time.perf_counter() - start, 1),
                    "trace": s.trace})
        save(rows)
        print(f"{v:9} after sign-off posted={s.posted} refused={[q for q, _ in s.refused]} "
              f"tools={row['tools']}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
