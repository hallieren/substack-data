"""Per-case paired table, baseline (08-26, 5 runs) beside the arm (3 runs),
majority verdicts, flips named, red-line hits per run. Reads analysis/gate.json
written by gate.py (no model calls here). Writes analysis/paired.md and
analysis/paired.json (the figure source).

Usage: uv run --project "$PICO" python <here>/paired.py
"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYM = {"pass": "✓", "fail": "✗", "invalid": "!"}


def majority(verdicts):
    v = [x for x in verdicts if x != "invalid"]
    if not v:
        return "none"
    return "pass" if sum(x == "pass" for x in v) * 2 > len(v) else "fail"


def main():
    g = json.loads((HERE / "analysis" / "gate.json").read_text())
    by = {"base": defaultdict(list), "arm": defaultdict(list)}
    for r in g["base_rows"]:
        by["base"][r["case"]].append(r)
    for r in g["arm_rows"]:
        by["arm"][r["case"]].append(r)
    cases = sorted(set(by["base"]) | set(by["arm"]))
    out, L = [], ["# Paired, per case", "",
                  "| case | sev | baseline r1..r5 | arm r1..r3 | majority before → after | red-line hits (arm) | arm failing checks |",
                  "|---|---|---|---|---|---|---|"]
    flips = []
    for cid in cases:
        b = sorted(by["base"][cid], key=lambda r: r["repeat"])
        a = sorted(by["arm"][cid], key=lambda r: r["repeat"])
        mb, ma = majority([r["verdict"] for r in b]), majority([r["verdict"] for r in a])
        flip = mb != ma and "none" not in (mb, ma)
        if flip:
            flips.append((cid, mb, ma))
        hits = [f"r{r['repeat']} {h}" for r in a for h in r["hits"]]
        fails = sorted({f for r in a for f in r["failing"]})
        sev = (b or a)[0]["sev"]
        out.append({"case": cid, "sev": sev,
                    "base": [r["verdict"] for r in b], "arm": [r["verdict"] for r in a],
                    "base_pass": sum(r["verdict"] == "pass" for r in b),
                    "arm_pass": sum(r["verdict"] == "pass" for r in a),
                    "majority_base": mb, "majority_arm": ma, "flip": flip,
                    "arm_hits": hits, "arm_failing": fails,
                    "base_hits": [f"r{r['repeat']} {h}" for r in b for h in r["hits"]]})
        L.append(f"| {cid} | {sev} | {' '.join(SYM[r['verdict']] for r in b)} | "
                 f"{' '.join(SYM[r['verdict']] for r in a)} | {mb} → {ma}{' FLIP' if flip else ''} | "
                 f"{', '.join(hits) or '—'} | {', '.join(fails) or '—'} |")
    L.append("")
    L.append(f"Majority flips: {len(flips)} of {len(cases)}: "
             + (", ".join(f"{c} {x}→{y}" for c, x, y in flips) or "none"))
    A, B = g["arm"], g["baseline"]
    L.append("")
    L.append(f"Pass rate baseline {B['pass']}/{B['valid']} = {B['pass_rate']:.1%}, "
             f"arm {A['pass']}/{A['valid']} = {A['pass_rate']:.1%}, half-width of the difference {g['half_width_diff']:.1%}")
    L.append(f"Cost P50/P95 baseline ${B['cost_p50']:.4f}/${B['cost_p95']:.4f}, arm ${A['cost_p50']:.4f}/${A['cost_p95']:.4f}")
    (HERE / "analysis" / "paired.md").write_text("\n".join(L) + "\n")
    (HERE / "analysis" / "paired.json").write_text(json.dumps(
        {"cases": out, "flips": flips, "arm": A, "baseline": B,
         "half_width_diff": g["half_width_diff"]}, indent=1))
    print("\n".join(L))


if __name__ == "__main__":
    main()
