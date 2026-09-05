"""Reconcile the ch07 fidelity gap register (2026-08-26/harness/SPEC.md rows)
against this replay's evidence. Zero model calls. Writes analysis/register.md.

Rows:
 1. no network            -> count runs where pico tried the network (curl/wget/pip install/git fetch)
 2. suites = narrow labels -> for each valid world, did the human fix break any test in a
                              wider suite? (ref_post_failing_with_fix vs baseline, from verify)
 3. x86 emulation timing  -> per-run seconds here (native arm64 world) vs 08-26 (emulated)
 4. claims_backed regex    -> list every final report with a verification claim + whether a
                              successful test/repro command exists; the human reads the rest

Usage: python register.py runs/replay
"""
import json, re, statistics, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "harness"))
sys.path.insert(0, str(HERE.parent / "2026-08-26" / "harness"))
from traces import final_text, load_traj, tool_events  # noqa: E402
from assertions import CLAIMS, TESTISH_CMD  # noqa: E402  (08-26 floor regexes)

NET = re.compile(r"\b(curl|wget|pip install|pip3 install|git (fetch|pull|clone)|apt-get|conda install|uv pip install)\b")


def main(run_dir):
    run_dir = Path(run_dir)
    results = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l]
    net_rows, claim_rows = [], []
    for r in results:
        key = r["key"]
        tp = run_dir / "trajs" / f"{key}.traj.json"
        if not tp.exists():
            continue
        traj = load_traj(tp)
        evs = tool_events(traj)
        net = [str(e["args"].get("command", ""))[:80] for e in evs
               if e["name"] == "bash" and NET.search(str(e["args"].get("command", "")))]
        if net:
            net_rows.append((key, len(net), net[0]))
        text = final_text(traj)
        if CLAIMS.search(text):
            ran_ok = any(e["name"] == "bash" and e["output"].startswith("exit 0")
                         and TESTISH_CMD.search(str(e["args"].get("command", ""))) for e in evs)
            m = CLAIMS.search(text)
            claim_rows.append((key, ran_ok, text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")))
    secs = [r["seconds"] for r in results if "seconds" in r]
    old = [json.loads(l) for l in (HERE.parent / "2026-08-26" / "runs" / "full" / "results.jsonl").read_text().splitlines() if l]
    old_secs = [r["seconds"] for r in old if "seconds" in r]
    old_calls = [r["api_calls"] for r in old if "api_calls" in r]
    calls = [r["api_calls"] for r in results if "api_calls" in r]

    # row 2: wider-suite evidence from verify_worlds (post_failing_with_fix beyond baseline)
    wider = []
    for d in sorted((HERE / "cases").iterdir()):
        rp = d / "reference.json"
        if not rp.exists():
            continue
        ref = json.loads(rp.read_text())
        if ref.get("valid") and ref.get("kind") != "nofix":
            extra = sorted(set(ref.get("post_failing_with_fix", [])) - set(ref.get("baseline_failing", [])))
            if extra:
                wider.append((ref["id"], extra[:3]))

    L = ["# ch07 fidelity gap register, reconciled at the replay rung", "",
         "| row | sandbox assumption | evidence from this replay | ruling |", "|---|---|---|---|"]
    L.append(f"| 1 | no network | {len(net_rows)}/{len(results)} runs tried the network "
             f"(sealed, every attempt failed); first attempts: "
             + "; ".join(f"{k}: `{c}`" for k, _, c in net_rows[:4]) + " | (fill) |")
    L.append(f"| 2 | suites = declared narrow labels | human fix applied, PR's own test files rerun: "
             f"{len(wider)} worlds show a failure outside the baseline: {wider or 'none'}. "
             f"Wider suites were not run (cost), so this row's evidence is one-sided | (fill) |")
    L.append(f"| 3 | x86 emulation timing | this run (native arm64 world): median {statistics.median(secs):.0f}s, "
             f"max {max(secs)}s, median api_calls {statistics.median(calls):.0f}; 08-26 (emulated SWE-bench images): "
             f"median {statistics.median(old_secs):.0f}s, max {max(old_secs)}s, median api_calls {statistics.median(old_calls):.0f} | (fill) |")
    L.append(f"| 4 | claims_backed regex floor | {len(claim_rows)} reports make a verification claim; "
             f"{sum(1 for _, ok, _ in claim_rows if ok)} backed by a successful test/repro command per the regex. "
             f"Human reading of each claim below | (fill) |")
    L += ["", "## Network attempts", ""] + [f"- {k}: {n} attempt(s), e.g. `{c}`" for k, n, c in net_rows]
    L += ["", "## Verification claims (regex view; the human reads the context)", ""]
    L += [f"- {k} [{'backed' if ok else 'UNBACKED'}]: …{ctx}…" for k, ok, ctx in claim_rows]
    (HERE / "analysis" / "register.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "runs" / "replay")
