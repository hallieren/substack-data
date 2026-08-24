#!/usr/bin/env python3
"""Judge-vs-human alignment report for the ch05 demo.

Inputs: evidence/blind-sheet.md (Hallie's blind labels, table cells filled)
        evidence/judge/judge-majority.json (majority of k judge runs)
Output: printed report + evidence/alignment-report.md

Layered by difficulty stratum; fixed per-class recall line; per-dimension
disagreement table. Deterministic: same files in, same report out.
"""
import json
import re
from pathlib import Path

EV = Path(__file__).resolve().parents[1]
DIMS = ["root-cause", "sibling-coverage", "verification-substance", "scope-discipline"]


def parse_sheet():
    rows = {}
    for line in (EV / "blind-sheet.md").read_text().splitlines():
        if not line.startswith("|") or line.startswith("| instance_id") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7 or not cells[0]:
            continue
        iid, stratum = cells[0], cells[1]
        dims = dict(zip(DIMS, [c.lower() for c in cells[2:6]]))
        overall = cells[6].lower()
        if overall:
            rows[iid] = {"stratum": stratum, "dims": dims, "overall": overall}
    return rows


def main():
    human = parse_sheet()
    judge = json.loads((EV / "judge" / "judge-majority.json").read_text())
    matched = sorted(set(human) & set(judge))
    if not matched:
        print("no labeled rows found in blind-sheet.md yet — fill the sheet first")
        return

    lines = [
        "# judge-vs-human alignment report (ch05 demo)",
        "",
        f"judge ruled {len(judge)} cases, human labeled {len(human)}, matched {len(matched)}",
        "",
    ]

    by_stratum = {}
    for iid in matched:
        by_stratum.setdefault(human[iid]["stratum"], []).append(iid)

    order = [">4 hours", "1-4 hours", "15 min - 1 hour", "<15 min fix"]
    for st in [s for s in order if s in by_stratum] + [s for s in by_stratum if s not in order]:
        ids = by_stratum[st]
        dis = [i for i in ids if human[i]["overall"] != judge[i]["verdict"]]
        lines.append(f"  {st}: {len(dis)}/{len(ids)} disagreement rate {len(dis)/len(ids):.2f}")
        for i in dis:
            lines.append(f"    - {i}: judge={judge[i]['verdict']} human={human[i]['overall']}")
    flagged = [i for i in matched if human[i]["overall"] in ("concern", "unsafe")]
    caught = [i for i in flagged if judge[i]["verdict"] in ("concern", "unsafe")]
    lines.append(
        f"  per-class recall: human labeled {len(flagged)} cases concern, judge caught {len(caught)}"
    )

    lines += ["", "per-dimension disagreement (matched cases where both ruled ok/flaw):"]
    for d in DIMS:
        both = [
            i for i in matched
            if human[i]["dims"].get(d) in ("ok", "flaw")
            and judge[i]["dims"].get(d) in ("ok", "flaw")
        ]
        dis = [i for i in both if human[i]["dims"][d] != judge[i]["dims"][d]]
        detail = " ".join(
            f"[{i}: judge={judge[i]['dims'][d]} human={human[i]['dims'][d]}]" for i in dis
        )
        n = len(both)
        rate = f"{len(dis)/n:.2f}" if n else "n/a"
        lines.append(f"  {d}: {len(dis)}/{n} disagreement rate {rate} {detail}")

    lines += [
        "",
        "Validity: labels from a second-model blind reader (Claude, different family",
        "from the judge), author arbitrates; no human labeler this round, so the",
        "human-human ceiling is unmeasured and judge-vs-human is really judge-vs-reader.",
        "Void the moment the judge prompt, the base model, or the rubric changes.",
    ]
    report = "\n".join(lines)
    print(report)
    (EV / "alignment-report.md").write_text(report + "\n")


if __name__ == "__main__":
    main()
