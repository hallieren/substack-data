"""stats — ch06's discipline: repeats, flip lists, and the wobble, never a
lone point. A case's run verdict = every declared assertion passes (a
pending_judge resolves through judge-red-justification; sev-1 never passes on
the judge alone — the judge can only settle the red-justification branch,
every other channel is deterministic)."""

import json
import math
from pathlib import Path

HARNESS = Path(__file__).resolve().parent

from assertions import check_case, newly_failing  # noqa: E402
from cases import issue_text, load_cases  # noqa: E402
from judge import judge_red_justification  # noqa: E402
from traces import final_text, load_traj  # noqa: E402


def evaluate_run(case: dict, run_dir: Path, repeat: int, use_judge: bool = True) -> dict:
    key = f"{case['id']}-r{repeat}"
    traj = load_traj(run_dir / "trajs" / f"{key}.traj.json")
    world = json.loads((run_dir / "world" / f"{key}.json").read_text())
    if world["status"].startswith(("container failed", "error", "wall clock", "world invalid")):
        # SPEC iron rule: a broken world raises an alarm, never a forced verdict
        return {"key": key, "case": case["id"], "repeat": repeat, "verdict": "invalid",
                "checks": {}, "sources": [], "status": world["status"]}
    checks = check_case(case, traj, world)
    sources = {"assertions"}
    for name, res in checks.items():
        if res["verdict"] == "pending_judge" and use_judge:
            sources.add("judge")
            j = judge_red_justification(
                issue_text(case), newly_failing(world), final_text(traj),
                run_dir / "judge-cache.json", key)
            res["verdict"] = "pass" if j["verdict"] == "legal" else "fail"
            res["evidence"] += f" -> judge: {j['verdict']} ({j['votes']})"
    verdict = "pass" if all(r["verdict"] == "pass" for r in checks.values()) else "fail"
    return {"key": key, "case": case["id"], "repeat": repeat, "verdict": verdict,
            "checks": checks, "sources": sorted(sources), "status": world["status"]}


def evaluate(run_dir: Path, repeats: int, use_judge: bool = True) -> dict:
    """Returns {case_id: {"case":..., "runs":[run verdicts]}}, plus totals."""
    out = {}
    for case in load_cases():
        runs = []
        for r in range(1, repeats + 1):
            if not (run_dir / "trajs" / f"{case['id']}-r{r}.traj.json").exists():
                continue
            runs.append(evaluate_run(case, run_dir, r, use_judge))
        if runs:
            out[case["id"]] = {"case": case, "runs": runs}
    return out


def wobble(p: float, n: int) -> float:
    """Half-width of the ~95% interval on a pass fraction over n case-runs."""
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / n) if n else 0.0


def flips(evaluated: dict) -> list[str]:
    return sorted(cid for cid, e in evaluated.items()
                  if len({r["verdict"] for r in e["runs"] if r["verdict"] != "invalid"}) > 1)
