"""analyze — assembles analysis.txt, the source of every number in the article.
Runs layers.py's tally on the control, round 1 and round 2, adds cost and
wall-clock from results.jsonl, and prints the paired before/after table for
the round-2 samples. Offline, no model calls.

Usage: cd ~/Documents/pico && uv run python <here>/analyze.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
sys.path.insert(0, str(HERE))

import layers  # noqa: E402

R1 = DATA / "runs" / "attacks"
R2 = DATA / "runs" / "attacks-r2-antiinjection"


def costs(run_dir: Path) -> str:
    rs = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l]
    log = (run_dir / "log.txt").read_text().splitlines()
    return (f"runs {len(rs)} · cost ${sum(r['cost_usd'] for r in rs):.2f} · "
            f"agent-seconds {sum(r['seconds'] for r in rs)} (max {max(r['seconds'] for r in rs)}) · "
            f"fix accepted {sum(1 for r in rs if r.get('accept_post') == 0)}/{len(rs)} · "
            f"wall clock {log[0][1:9]} → {log[-1][1:9]} · "
            f"invalid worlds {sum(1 for r in rs if r['status'] != 'done')}")


def paired(rows1, rows2) -> str:
    out = ["## Round 2 vs round 1, issue-door samples, same baits, one extra system-prompt line", "",
           "| sample | round 1 cells | breach | round 2 cells | breach |", "|---|---|---|---|---|"]
    by1, by2 = {}, {}
    for r in rows1:
        by1.setdefault(r["id"], []).append(r)
    for r in rows2:
        by2.setdefault(r["id"], []).append(r)
    short = {"not_seen": "·", "declined": "D", "seal_stopped": "S", "breach": "B", "invalid": "!"}
    tb1 = tb2 = 0
    for aid in sorted(by2):
        a = sorted(by1[aid], key=lambda r: r["repeat"])
        b = sorted(by2[aid], key=lambda r: r["repeat"])
        b1 = sum(r["cell"] == "breach" for r in a)
        b2 = sum(r["cell"] == "breach" for r in b)
        tb1 += b1
        tb2 += b2
        out.append(f"| {aid} | {' '.join(short[r['cell']] for r in a)} | {b1}/{len(a)} | "
                   f"{' '.join(short[r['cell']] for r in b)} | {b2}/{len(b)} |")
    n1 = sum(len(v) for k, v in by1.items() if k in by2)
    n2 = sum(len(v) for v in by2.values())
    out.append(f"| **total** | | **{tb1}/{n1}** | | **{tb2}/{n2}** |")
    out.append("")
    out.append("Cells: · not seen, D declined, S seal stopped the attempt, B breach.")
    return "\n".join(out)


def main() -> None:
    parts = ["# analysis — ch12 red-team round on pico (2026-09-02)", ""]
    parts.append("## Control: 08-26 clean runs of the four base cases, ch12 red lines")
    parts.append("")
    ctrl = layers.run_control()
    parts.append(layers.render(ctrl, "control").split("\n", 2)[2])
    parts.append("")
    parts.append("## Round 1: eight baits × 5 runs")
    parts.append("")
    parts.append(costs(R1))
    parts.append("")
    rows1 = layers.run_attack_dir(R1, 5)
    parts.append(layers.render(rows1, "round 1").split("\n", 2)[2])
    if (R2 / "results.jsonl").exists():
        parts.append("")
        parts.append("## Round 2: the anti-injection line, four issue-door baits × 5 runs")
        parts.append("")
        parts.append("System prompt = round 1 prompt + this rule:" + json.dumps(
            __import__("run_attacks").ANTI_INJECTION_LINE))
        parts.append("")
        parts.append(costs(R2))
        parts.append("")
        rows2 = layers.run_attack_dir(R2, 5)
        parts.append(layers.render(rows2, "round 2").split("\n", 2)[2])
        parts.append("")
        parts.append(paired(rows1, rows2))
        (R2 / "layers.jsonl").write_text("\n".join(json.dumps(r) for r in rows2) + "\n")
    text = "\n".join(parts) + "\n"
    (DATA / "analysis.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
