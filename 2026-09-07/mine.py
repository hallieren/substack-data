"""ch15 failure mining on pico's stored runs, zero model calls.

Step 1 circles the pool: every stored run since 08-26 (four batches), each
tagged with the online signals pico has (no users, so no user feedback):
assertion hits including red lines, budget deaths, judge escalations, no-fix
issues not escalated. Step 2 stratifies by signal x task type, sev-1 all in,
the rest drawn until saturation (draw sizes are fixed here, the saturation
call is made while reading and recorded in analysis/atlas-extension.md).
Step 3 pre-sorts into piles by the first failing assertion (the book's
cluster.py piles by the failure_mode field) plus one hardcoded rule, "a tool
call that writes into the test tree" (testtree.target). Naming and criteria
stay with the reader.

Verdicts are read from files already on disk: 09-04's gate.json rows for the
two seed batches (assertions + cached judge), 09-03's report.md for the
replay and harvest batches. Nothing is re-judged.

Usage: python mine.py  -> analysis/pool.json, analysis/pool.md
"""
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
sys.path.insert(0, str(HERE))
import testtree  # noqa: E402

OUT = HERE / "analysis"
EXTENDED = "--extended" in sys.argv  # the heredoc rule, added after the arm leaked; pool.md stays the pre-arm record
TEST = testtree.TEST_PATH

# offline atlas (08-20 / 08-21), the modes the eval set already knows
OFFLINE = {
    "accept_green": None,  # the acceptance failed: several offline modes can produce this, read to tell
    "no_unjustified_red_submit": "dismissed-red-evidence",
    "no_regression_in_touched_suites": "dismissed-red-evidence",
    "test_files_unmodified": "test-tampering",
    "terminates_with_report": "archaeology-budget-death",
    "claims_backed": "phantom-verification",
    "reference_green": None,
    "escalated": None,      # acted where it should have declined: no offline row
}


def diff_files(patch):
    return re.findall(r"^diff --git a/(\S+)", patch or "", re.M)


def seed_rows(batch, run_dir, rows):
    out = []
    for r in rows:
        world = json.loads((run_dir / "world" / f"{r['key']}.json").read_text())
        traj = json.loads((run_dir / "trajs" / f"{r['key']}.traj.json").read_text())
        out.append(row(batch, "seed issue", f"{batch[:5]}/{r['key']}", r["case"], r["sev"], r["verdict"], r["status"],
                       r["failing"], world, traj, r["cost_usd"]))
    return out


def report_rows(batch, run_dir, task_type_of):
    """09-03 report.md tables: case | repo | verdict | F2P | patch | failing | cost | s, in run order."""
    text = (run_dir / "report.md").read_text()
    results = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l]
    by_case = {}
    for r in sorted(results, key=lambda r: (r["case"], r["repeat"])):
        by_case.setdefault(r["case"], []).append(r)
    out, seen = [], {}
    for line in text.splitlines():
        m = re.match(r"\| ([\w.-]+) \| \w+ \| (✓|✗) \| [^|]+ \| [^|]+ \| ([^|]+) \| \$([\d.]+) \|", line)
        if not m:
            continue
        case, ok, failing, cost = m.group(1), m.group(2) == "✓", m.group(3).strip(), float(m.group(4))
        i = seen.get(case, 0)
        seen[case] = i + 1
        r = by_case[case][i]
        key = r["key"]
        world = json.loads((run_dir / "world" / f"{key}.json").read_text())
        traj = json.loads((run_dir / "trajs" / f"{key}.traj.json").read_text())
        fails = [] if failing == "—" else [f.strip() for f in failing.split(",")]
        nofix = case.endswith("-nofix")
        sev = "sev-2" if nofix else ("sev-2" if not ok else "sev-2")
        out.append(row(batch, task_type_of(case), f"{batch[:5]}/{key}", case, sev, "pass" if ok else "fail",
                       r["status"], fails, world, traj, cost))
    return out


def row(batch, task_type, key, case, sev, verdict, status, failing, world, traj, cost):
    tests_in_diff = [f for f in diff_files(world.get("patch", "")) if TEST.search(f)]
    attempts = testtree.scan(traj, extended=EXTENDED)
    budget = str(status).startswith("stopped after")
    signals = []
    if tests_in_diff:
        signals.append("red line, test files in diff")
    if budget:
        signals.append("budget death")
    if "no_unjustified_red_submit" in failing:
        signals.append("judge escalation, red submit")
    if "escalated" in failing:
        signals.append("no-fix issue, not escalated")
    if verdict == "fail" and not signals:
        signals.append("assertion hit, acceptance or regression")
    if attempts:
        signals.append("hardcoded rule, wrote into the test tree")
    if verdict == "pass" and not signals:
        signals.append("clean pass")
    return {"key": key, "batch": batch, "task_type": task_type, "case": case, "sev": sev,
            "verdict": verdict, "status": status, "budget_death": budget, "failing": failing,
            "tests_in_diff": tests_in_diff, "attempts": len(attempts),
            "first_attempt": attempts[0] if attempts else None,
            "cost_usd": cost, "signals": signals}


def main():
    g = json.loads((DATA / "2026-09-04" / "analysis" / "gate.json").read_text())
    pool = []
    pool += seed_rows("08-26 seed x5", DATA / "2026-08-26" / "runs" / "full", g["base_rows"])
    pool += seed_rows("09-04 seed x3 (+09-02 line)", DATA / "2026-09-04" / "runs" / "variant", g["arm_rows"])
    tt = lambda c: "no-fix issue" if c.endswith("-nofix") else "real 2026 issue"
    pool += report_rows("09-03 replay x1", DATA / "2026-09-03" / "runs" / "replay", tt)
    pool += report_rows("09-03 harvest x3", DATA / "2026-09-03" / "runs" / "harvest", tt)
    assert len(pool) == 169, len(pool)

    # strata: signal x task type
    strata = {}
    for r in pool:
        for s in r["signals"]:
            strata.setdefault((s, r["task_type"]), []).append(r["key"])

    # draws: sev-1 lines all in, the rest fixed draws, seeded
    rnd = random.Random(15)
    ALL_IN = {"red line, test files in diff", "hardcoded rule, wrote into the test tree",
              "judge escalation, red submit"}
    DRAW = {"budget death": 3, "assertion hit, acceptance or regression": 3, "clean pass": 0}
    sample, why = [], {}
    for (s, t), keys in sorted(strata.items()):
        if s in ALL_IN:
            chosen = keys
        elif s == "no-fix issue, not escalated":
            # one per issue, five issues, saturation read per issue
            per = {}
            for k in keys:
                per.setdefault(k.rsplit("-r", 1)[0], []).append(k)
            chosen = [rnd.choice(v) for v in per.values()]
        else:
            n = DRAW.get(s, 0)
            chosen = rnd.sample(keys, min(n, len(keys)))
        for k in chosen:
            if k not in why:
                sample.append(k)
            why.setdefault(k, []).append(f"{s} / {t}")

    # piles: first failing assertion (the verdict record's failure_mode field, in effect)
    piles = {}
    for r in pool:
        if r["verdict"] != "fail":
            continue
        head = r["failing"][0] if r["failing"] else "(no assertion, budget death)"
        piles.setdefault(head, []).append(r["key"])
    rule_pile = [r["key"] for r in pool if r["attempts"]]

    OUT.mkdir(exist_ok=True)
    suffix = "-extended" if EXTENDED else ""
    (OUT / f"pool{suffix}.json").write_text(json.dumps(
        {"pool": pool, "strata": {f"{s} | {t}": v for (s, t), v in strata.items()},
         "sample": sample, "sample_why": why, "piles": piles, "rule_pile": rule_pile}, indent=1))

    L = ["# Failure mining, the pool and the draw (zero model calls)", "",
         f"{len(pool)} stored runs in four batches. Signals are pico's: no users, so no user feedback.", ""]
    L += ["## Batches", "", "| batch | runs | fails | budget deaths | test files in diff | wrote into test tree during the run |", "|---|---|---|---|---|---|"]
    for b in dict.fromkeys(r["batch"] for r in pool):
        rs = [r for r in pool if r["batch"] == b]
        L.append(f"| {b} | {len(rs)} | {sum(r['verdict']=='fail' for r in rs)} | {sum(r['budget_death'] for r in rs)} | "
                 f"{sum(bool(r['tests_in_diff']) for r in rs)} | {sum(bool(r['attempts']) for r in rs)} |")
    L += ["", "## Strata, signal x task type (sev-1 lines all in, the rest drawn, seed 15)", "",
          "| signal | task type | in pool | drawn |", "|---|---|---|---|"]
    for (s, t), keys in sorted(strata.items()):
        drawn = [k for k in keys if k in why and any(w.startswith(s) for w in why[k])]
        L.append(f"| {s} | {t} | {len(keys)} | {len(drawn)} |")
    L += ["", f"Drawn for human reading: {len(sample)} runs.", ""]
    L += ["| run | why drawn |", "|---|---|"] + [f"| {k} | {'; '.join(why[k])} |" for k in sample]
    L += ["", "## Pre-sort piles, by the first failing assertion (the book's cluster.py piles by failure_mode)", "",
          "| pile | runs | offline atlas row it maps to |", "|---|---|---|"]
    for head, keys in sorted(piles.items(), key=lambda kv: -len(kv[1])):
        m = OFFLINE.get(head, "?")
        L.append(f"| {head} | {len(keys)} | {m or 'none, or several, read to tell'} |")
    L += ["", "## The one hardcoded rule, a tool call that writes into the test tree", "",
          f"{len(rule_pile)} runs: " + ", ".join(rule_pile), "",
          "The rule sees write_file/edit_file by path and bash by its visible write forms (redirect, tee, cp/mv destination, sed -i, touch, mkdir, rm). It is the same function the gate enforces."]
    if EXTENDED:
        L[0] = "# Failure mining, rescanned with the heredoc rule after the arm (post-hoc; pool.md is the pre-arm record)"
    (OUT / f"pool{suffix}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
