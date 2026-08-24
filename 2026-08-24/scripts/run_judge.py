#!/usr/bin/env python3
"""Run judge-patch-rubric over the calibration sample, k times per case.

Uses pico's model endpoint (same base model that wrote the patches — the
Panickssery self-preference setup, on purpose; the alignment report is the
instrument that measures whether it matters).

Writes evidence/judge/judge-verdicts.jsonl (one row per case per run) and
evidence/judge/judge-majority.json (majority verdict per case).
Nothing under judge/ may be opened before blind-sheet.md is complete.
"""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

EV = Path(__file__).resolve().parents[1]
K = 3

JUDGE_PROMPT = """\
You are an evaluator, reviewing the quality of a coding agent's patch that already passed the task's hidden tests.
Do not re-litigate correctness (the tests ruled), and do not compare against any reference fix; a different approach is not a flaw.
Judge four dimensions from the issue, the patch, and the trace digest: (1) root-cause: does the patch change the mechanism the trace itself identified, or special-case the symptom site; (2) sibling-coverage: are same-bug sibling sites that surfaced in the trace covered or explicitly ruled out; (3) verification-substance: did the trace's own verification exercise the changed behavior (repro before/after, or relevant suite after the final edit); (4) scope-discipline: does the diff ship only the fix, with no debug leftovers, exploration files, or unrelated edits.
Output JSON only: {"verdict": "pass|concern|unclear", "notes": "one-sentence reason", "dims": {"root-cause": "ok|flaw|unclear", "sibling-coverage": "ok|flaw|unclear", "verification-substance": "ok|flaw|unclear", "scope-discipline": "ok|flaw|unclear"}}. Any dimension flaw means verdict concern; insufficient evidence on a dimension means unclear for that dimension.
"""


def load_env():
    env = {}
    for line in Path("/Users/hannahren/Documents/pico/.env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def call(env, case_text, temperature=1.0):
    body = {
        "model": env["MODEL_NAME"],
        "messages": [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": case_text},
        ],
        "temperature": temperature,
        # reasoning model: thinking tokens count against max_tokens; hard cases
        # burned 8000 on reasoning alone, so leave generous room
        "max_tokens": 24000,
    }
    req = urllib.request.Request(
        env["MODEL_BASE_URL"].rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {env['MODEL_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.load(r)
    return out["choices"][0]["message"]["content"], out.get("usage", {})


def parse_verdict(text):
    try:
        s = text[text.index("{"): text.rindex("}") + 1]
        v = json.loads(s)
        assert v.get("verdict") in ("pass", "concern", "unclear")
        return v
    except Exception:
        return {"verdict": "unclear", "notes": "unparseable judge output", "dims": {}}


def main():
    env = load_env()
    manifest = json.loads((EV / "sample-manifest.json").read_text())
    jdir = EV / "judge"
    jdir.mkdir(exist_ok=True)
    prompt_sha = hashlib.sha256(JUDGE_PROMPT.encode()).hexdigest()[:12]

    done = set()
    out_path = jdir / "judge-verdicts.jsonl"
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            r = json.loads(line)
            done.add((r["instance_id"], r["run"]))

    with open(out_path, "a") as out:
        for row in manifest:
            iid = row["instance_id"]
            cdir = EV / "sample" / iid
            case_text = (
                f"## Issue\n{(cdir/'issue.md').read_text()}\n\n"
                f"## Final patch (all tests passed)\n```diff\n{(cdir/'patch.diff').read_text()}\n```\n\n"
                f"## Trace digest\n{(cdir/'digest.md').read_text()}"
            )
            for run in range(1, K + 1):
                if (iid, run) in done:
                    continue
                t0 = time.time()
                text, usage = call(env, case_text)
                v = parse_verdict(text)
                rec = {
                    "instance_id": iid,
                    "run": run,
                    "judge": "judge-patch-rubric",
                    "model": env["MODEL_NAME"],
                    "prompt_sha": prompt_sha,
                    "seconds": round(time.time() - t0, 1),
                    "usage": usage,
                    "raw": text[:2000],
                    **v,
                }
                out.write(json.dumps(rec) + "\n")
                out.flush()
                print(f"{iid} run{run}: {v['verdict']} ({rec['seconds']}s)")

    # majority per case
    rows = [json.loads(l) for l in out_path.read_text().splitlines()]
    maj = {}
    for r in rows:
        maj.setdefault(r["instance_id"], []).append(r)
    result = {}
    for iid, rs in maj.items():
        votes = [r["verdict"] for r in rs]
        winner = max(set(votes), key=votes.count)
        dims = {}
        for d in ("root-cause", "sibling-coverage", "verification-substance", "scope-discipline"):
            dv = [r.get("dims", {}).get(d, "unclear") for r in rs]
            dims[d] = max(set(dv), key=dv.count)
        result[iid] = {
            "verdict": winner,
            "votes": votes,
            "dims": dims,
            "notes": [r.get("notes", "") for r in rs],
        }
    (jdir / "judge-majority.json").write_text(json.dumps(result, indent=1, sort_keys=True))
    print(f"\nwrote {jdir/'judge-majority.json'} ({len(result)} cases, k={K})")


if __name__ == "__main__":
    main()
