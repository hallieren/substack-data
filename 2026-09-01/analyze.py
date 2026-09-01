"""Final analysis of the three-arm reviewer experiment (ch11 article).

Reads the raw reviews.jsonl files from the pico repo runs, keeps the latest
row per (instance, arm, repeat) cell, and prints every number the article
uses: approval rates with Wilson 95% intervals, per-mode breakdown, probe
results, confidence distributions, tool-call stats, flip rates, and the cost
ledger. Run: python3 analyze.py
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

PICO = Path("~/Documents/pico/bench/runs").expanduser()
SOURCES = {
    "main": [PICO / "review-full-20260901/reviews.jsonl",
             PICO / "review-full-20260901-c/reviews.jsonl"],
    "probes": [PICO / "review-probes-20260901/reviews.jsonl"],
}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def load(paths) -> list[dict]:
    cells = {}
    for path in paths:
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                cells[(r["instance_id"], r["arm"], r["repeat"])] = r
    return list(cells.values())


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*k/n:.0f}% [{100*lo:.0f}, {100*hi:.0f}]" if n else "n/a"


def main() -> None:
    rows = load(SOURCES["main"])
    probes = [r for r in load(SOURCES["probes"]) if r.get("verdict")]
    no_verdict = [r for r in rows if not r.get("verdict")]
    rows = [r for r in rows if r.get("verdict")]
    print(f"cells with verdict: {len(rows)}, without: {len(no_verdict)}")
    for r in no_verdict:
        print("  no verdict:", r["instance_id"], r["arm"], f"r{r['repeat']}", r["status"][:60])

    print("\n== headline: per arm ==")
    for arm in "ABC":
        bad = [r for r in rows if r["arm"] == arm and not r["resolved"]]
        good = [r for r in rows if r["arm"] == arm and r["resolved"]]
        ba = sum(r["verdict"] == "approve" for r in bad)
        gr = sum(r["verdict"] == "reject" for r in good)
        pa = [r for r in probes if r["arm"] == arm]
        pr = sum(r["verdict"] == "reject" for r in pa)
        print(f"arm {arm}: bad approved {pct(ba, len(bad))} | good rejected {pct(gr, len(good))}"
              f" | probes rejected {pr}/{len(pa)}")

    print("\n== bad-patch approval by failure mode ==")
    modes = sorted({r["mode"] for r in rows if r["mode"]})
    for mode in modes:
        line = f"{mode}: "
        for arm in "ABC":
            sel = [r for r in rows if r["arm"] == arm and r["mode"] == mode]
            a = sum(r["verdict"] == "approve" for r in sel)
            line += f"  {arm} {a}/{len(sel)}"
        print(line)

    print("\n== confidence on WRONG approvals (bad patches) ==")
    for arm in "ABC":
        c = Counter(r["confidence"] for r in rows
                    if r["arm"] == arm and not r["resolved"] and r["verdict"] == "approve")
        print(f"arm {arm}: {dict(c)}")

    print("\n== arm C tool calls ==")
    cbad = [r for r in rows if r["arm"] == "C" and not r["resolved"]]
    ap = [r["evidence_tool_calls"] for r in cbad if r["verdict"] == "approve"]
    re_ = [r["evidence_tool_calls"] for r in cbad if r["verdict"] == "reject"]
    for name, xs in [("approve(bad)", ap), ("reject(bad)", re_)]:
        if xs:
            xs2 = sorted(xs)
            print(f"{name}: n={len(xs)} median={xs2[len(xs2)//2]} min={xs2[0]} max={xs2[-1]}"
                  f" zero-tool={sum(x == 0 for x in xs)}")

    print("\n== flip rate across 3 repeats (instances with mixed verdicts, per arm) ==")
    for arm in "ABC":
        by_inst = defaultdict(set)
        for r in rows:
            if r["arm"] == arm:
                by_inst[r["instance_id"]].add(r["verdict"])
        mixed = [i for i, v in by_inst.items() if len(v) > 1]
        print(f"arm {arm}: {len(mixed)}/{len(by_inst)} instances flip: {sorted(mixed)}")

    print("\n== cost ledger (per review, USD) ==")
    for arm in "ABC":
        xs = sorted(r["cost_usd"] for r in rows if r["arm"] == arm)
        secs = sorted(r["seconds"] for r in rows if r["arm"] == arm)
        n = len(xs)
        print(f"arm {arm}: mean ${sum(xs)/n:.4f} median ${xs[n//2]:.4f} p95 ${xs[int(n*0.95)]:.4f}"
              f" | seconds median {secs[n//2]} p95 {secs[int(n*0.95)]}")
    total = sum(r["cost_usd"] for r in rows) + sum(r["cost_usd"] for r in probes)
    print(f"total spend, main + probes: ${total:.2f}")

    print("\n== the confessing report: astropy__astropy-13398 (M1) ==")
    for r in sorted((r for r in rows if r["instance_id"] == "astropy__astropy-13398"),
                    key=lambda r: (r["arm"], r["repeat"])):
        print(f"  arm {r['arm']} r{r['repeat']}: {r['verdict']}/{r['confidence']}"
              f" tools={r['evidence_tool_calls']}")


if __name__ == "__main__":
    main()
