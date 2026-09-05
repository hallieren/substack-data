"""runner — the ch07 runner pointed at production traffic (ch13 replay rung).

Differences from 2026-08-26/harness/runner.py, and nothing else:
  * the world is pico-world:<id> (cloned at the closing PR's base commit,
    built by build_worlds.py) instead of a prebuilt SWE-bench image;
  * the verdict source is the human fix's tests (reference.py) instead of a
    hand-written accept.py: after pico's run, the PR's test patch is applied
    on top of pico's state and the suites rerun;
  * repeat defaults to 1: production serves every ticket once.

Usage (from the pico repo, so `pico` imports resolve):
  cd ~/Documents/pico && uv run python <here>/runner.py <run_dir> [--repeat N] [case_id ...]
"""

import asyncio
import json
import sys
import time
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
DATA = HARNESS.parent
sys.path[:0] = [str(HARNESS), str(Path.home() / "Documents/pico/bench")]

from swebench_mini import (  # noqa: E402
    MAX_SPEND_TOKENS, MAX_TURNS, SYSTEM, TASK, _docker, container_tools,
    cost_usd, make_traj, seal_git,
)
from cases import issue_text, load_cases  # noqa: E402
from reference import suite_commands, parse_results, failing  # noqa: E402

from pico.loop import Stopped, run  # noqa: E402
from pico.providers import build_provider  # noqa: E402
from pico.types import Usage, user  # noqa: E402

CONCURRENCY = 6
WALL_CLOCK = 3600


async def sh(cid, command, timeout):
    wrapped = f"source /opt/miniconda3/bin/activate testbed && cd /testbed && {{ {command}\n}}"
    try:
        return await _docker("exec", cid, "bash", "-c", wrapped, timeout=timeout)
    except TimeoutError:
        return 124, f"killed: no completion within {timeout}s"


async def push_file(cid, path, content):
    code, out = await _docker("exec", "-i", cid, "bash", "-c", f"cat > {path}",
                              stdin=content.encode(), timeout=60)
    if code != 0:
        raise RuntimeError(f"push {path}: {out.strip()[:200]}")


async def existing(cid, paths):
    _, out = await sh(cid, "for p in " + " ".join(f"'{p}'" for p in paths)
                      + "; do [ -e \"$p\" ] && echo \"$p\"; done; true", 60)
    return set(out.split())


async def run_suites(cid, case):
    ex = await existing(cid, case["test_files"])
    results = {}
    for c in suite_commands(case["repo"], case["test_files"], ex):
        _, out = await sh(cid, c, 1500)
        results.update(parse_results(out))
    return results


async def run_one(case, repeat, run_dir):
    key = f"{case['id']}-r{repeat}"
    cid = f"pico-h13-{key}"
    started = time.time()
    spent, api_calls = Usage(), 0
    status, patch, new_msgs = "done", "", []
    world = {"baseline_failing": [], "post_failing": [], "ref_apply": None,
             "ref_results": {}, "patch": "", "status": ""}

    await _docker("rm", "-f", cid, timeout=60)
    code, out = await _docker("run", "-d", "--network", "none", "--name", cid, case["image"],
                              "tail", "-f", "/dev/null", timeout=600)
    if code != 0:
        status = f"container failed: {out.strip()[:200]}"
    else:
        seal_code, seal_out = await seal_git(cid, case["base_sha"])
        if seal_code != 0:
            status = f"error: git seal failed: {seal_out.strip()[:200]}"

    task_text = TASK.format(problem_statement=issue_text(case))
    if status == "done":
        try:
            world["baseline_failing"] = failing(await run_suites(cid, case))

            def count(u):
                nonlocal spent, api_calls
                spent, api_calls = spent + u, api_calls + 1

            try:
                new_msgs = await run(build_provider(), SYSTEM, [user(task_text)],
                                     container_tools(cid), max_turns=MAX_TURNS,
                                     max_spend_tokens=MAX_SPEND_TOKENS, on_usage=count)
            except Stopped as e:
                status, new_msgs = str(e), e.messages
            await _docker("exec", "-w", "/testbed", cid, "git", "add", "-N", ".", timeout=120)
            _, patch = await _docker("exec", "-w", "/testbed", cid, "git", "diff",
                                     timeout=120, merge_stderr=False)
            world["post_failing"] = failing(await run_suites(cid, case))
            # reference: the human fix's tests on top of pico's final state
            if case["test_patch"].strip():
                await push_file(cid, "/tmp/test.patch", case["test_patch"])
                world["ref_apply"], _ = await sh(cid, "git apply --whitespace=nowarn /tmp/test.patch || git apply --ignore-whitespace --whitespace=nowarn /tmp/test.patch", 120)
                if world["ref_apply"] == 0:
                    world["ref_results"] = await run_suites(cid, case)
        except Exception as e:
            status = f"error: {type(e).__name__}: {e}"
    await _docker("rm", "-f", cid, timeout=120)

    world["patch"], world["status"] = patch, status
    config = {"agent": "pico", "harness": "ch13-replay", "case": case["id"], "repeat": repeat,
              "world": case["image"], "base_sha": case["base_sha"], "network": "none",
              "git_seal": "timesafe-v1", "issue": case["url"]}
    traj = make_traj(instance_id=key, system=SYSTEM, task_text=task_text, new_messages=new_msgs,
                     exit_status=status, patch=patch, spent=spent, api_calls=api_calls, config=config)
    (run_dir / "trajs").mkdir(parents=True, exist_ok=True)
    (run_dir / "world").mkdir(parents=True, exist_ok=True)
    (run_dir / "trajs" / f"{key}.traj.json").write_text(json.dumps(traj, indent=1))
    (run_dir / "world" / f"{key}.json").write_text(json.dumps(world, indent=1))
    f2p = case["reference"]["f2p"]
    f2p_green = sum(world["ref_results"].get(t) == "PASSED" for t in f2p)
    return {"key": key, "case": case["id"], "repeat": repeat, "status": status,
            "seconds": round(time.time() - started), "api_calls": api_calls,
            "cost_usd": round(cost_usd(spent), 6), "f2p_green": f2p_green, "f2p_total": len(f2p),
            "newly_failing": sorted(set(world["post_failing"]) - set(world["baseline_failing"])),
            "patch_bytes": len(patch)}


async def main():
    args = list(sys.argv[1:])
    repeat = 1
    if "--repeat" in args:
        i = args.index("--repeat")
        repeat = int(args[i + 1])
        del args[i:i + 2]
    run_dir = Path(args[0]).resolve()
    only = set(args[1:])
    run_dir.mkdir(parents=True, exist_ok=True)
    cases = [c for c in load_cases() if not only or c["id"] in only]

    results_path = run_dir / "results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(l)["key"] for l in results_path.read_text().splitlines() if l}
    todo = [(c, r) for c in cases for r in range(1, repeat + 1) if f"{c['id']}-r{r}" not in done]
    log_file = (run_dir / "log.txt").open("a")

    def log(msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        log_file.write(line + "\n")
        log_file.flush()

    log(f"replay run: {len(todo)} to do ({len(cases)} cases x {repeat}), {len(done)} done")
    sem = asyncio.Semaphore(CONCURRENCY)
    finished = 0

    async def one(case, r):
        nonlocal finished
        async with sem:
            key = f"{case['id']}-r{r}"
            log(f"start {key}")
            try:
                row = await asyncio.wait_for(run_one(case, r, run_dir), WALL_CLOCK)
            except (TimeoutError, asyncio.TimeoutError):
                await _docker("rm", "-f", f"pico-h13-{key}", timeout=120)
                row = {"key": key, "case": case["id"], "repeat": r,
                       "status": f"wall clock: no finish in {WALL_CLOCK}s"}
            with results_path.open("a") as f:
                f.write(json.dumps(row) + "\n")
            finished += 1
            log(f"done {key} [{finished}/{len(todo)}] {row['status']} {row.get('seconds', '?')}s "
                f"f2p={row.get('f2p_green')}/{row.get('f2p_total')} ${row.get('cost_usd')}")

    await asyncio.gather(*(one(c, r) for c, r in todo))
    log("run complete")


if __name__ == "__main__":
    asyncio.run(main())
