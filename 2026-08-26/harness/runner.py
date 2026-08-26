"""runner — reads cases, resets the world, runs pico, collects traces.

The world is the sealed SWE-bench container (network off, git truncated by the
same seal as the 2026-08-15 run); reset = a fresh container from the image, so
every repeat starts from a byte-identical world. The model API is never
stubbed — the model is the thing under test.

Per (case, repeat):
  reset world -> setup -> accept must be RED pre-fix (world validity; a green
  pre-fix accept means the case is broken, the agent never takes the field) ->
  baseline the declared suites -> run pico -> git diff -> rerun accept and
  suites -> write trace + world probes.

Usage (from the pico repo, so `pico` imports resolve):
  cd ~/Documents/pico && uv run python <here>/runner.py <run_dir> [--repeat N] [case_id ...]
"""

import asyncio
import json
import re
import sys
import time
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
DATA = HARNESS.parent
sys.path[:0] = [str(HARNESS), str(Path.home() / "Documents/pico/bench")]

from swebench_mini import (  # noqa: E402
    MAX_SPEND_TOKENS, MAX_TURNS, SYSTEM, TASK, _docker, container_tools,
    cost_usd, image, make_traj, seal_git,
)

from cases import issue_text, load_cases  # noqa: E402

from pico.loop import Stopped, run  # noqa: E402
from pico.providers import build_provider  # noqa: E402
from pico.types import Usage, user  # noqa: E402

CONCURRENCY = 6
WALL_CLOCK = 3000  # agent loop + probes; probes on django suites are minutes

PYTEST_FAIL = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.M)
DJANGO_FAIL = re.compile(r"^(?:FAIL|ERROR):\s+(\S+)\s+\(([^)]+)\)", re.M)


def parse_failures(parser: str, output: str) -> list[str]:
    if parser == "django":
        return sorted({f"{m.group(2)}.{m.group(1)}" for m in DJANGO_FAIL.finditer(output)})
    return sorted({m.group(1) for m in PYTEST_FAIL.finditer(output)})


async def sh(cid: str, command: str, timeout: float) -> tuple[int, str]:
    wrapped = f"source /opt/miniconda3/bin/activate testbed && cd /testbed && {{ {command}\n}}"
    try:
        return await _docker("exec", cid, "bash", "-c", wrapped, timeout=timeout)
    except TimeoutError:
        return 124, f"killed: no completion within {timeout}s"


async def push_file(cid: str, path: str, content: str) -> None:
    code, out = await _docker("exec", "-i", cid, "bash", "-c", f"cat > {path}",
                              stdin=content.encode(), timeout=60)
    if code != 0:
        raise RuntimeError(f"push {path}: {out.strip()[:200]}")


async def run_suites(cid: str, suites: dict | None) -> list[str]:
    if not suites:
        return []
    _, out = await sh(cid, suites["cmd"], timeout=1800)
    return parse_failures(suites["parser"], out)


async def run_one(case: dict, repeat: int, run_dir: Path, base_commit: str) -> dict:
    key = f"{case['id']}-r{repeat}"
    cid = f"pico-h7-{key}"
    started = time.time()
    spent, api_calls = Usage(), 0
    status, patch, new_msgs = "done", "", []
    world = {"accept_pre": None, "accept_post": None,
             "baseline_failing": [], "post_failing": [], "patch": "", "status": ""}

    await _docker("rm", "-f", cid, timeout=60)
    img = image(case["instance_id"])
    code, out = await _docker("run", "-d", "--network", "none", "--name", cid, img,
                              "tail", "-f", "/dev/null", timeout=1800)
    if code != 0:
        img = img.replace(".arm64.", ".x86_64.")
        code, out = await _docker("run", "-d", "--network", "none",
                                  "--platform", "linux/amd64", "--name", cid, img,
                                  "tail", "-f", "/dev/null", timeout=3600)
    if code != 0:
        status = f"container failed: {out.strip()[:200]}"
    else:
        seal_code, seal_out = await seal_git(cid, base_commit)
        if seal_code != 0:
            status = f"error: git seal failed: {seal_out.strip()[:200]}"

    task_text = TASK.format(problem_statement=issue_text(case))
    if status == "done":
        try:
            for cmd in case["setup_cmds"]:
                sc, so = await sh(cid, cmd, 120)
                if sc != 0:
                    raise RuntimeError(f"setup `{cmd}`: {so.strip()[:200]}")
            await push_file(cid, "/tmp/accept.py", case["accept_py"])
            # accept.py contract: exit 0 = accepted, 1 = not met, else = probe broken
            world["accept_pre"], pre_out = await sh(cid, "python /tmp/accept.py", 900)
            if world["accept_pre"] == 0:
                status = "world invalid: accept green pre-fix"
            elif world["accept_pre"] != 1:
                status = f"world invalid: accept script broken (exit {world['accept_pre']}): " \
                         + pre_out.strip()[-200:]
            else:
                world["baseline_failing"] = await run_suites(cid, case["suites"])

                def count(u: Usage) -> None:
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
                world["accept_post"], _ = await sh(cid, "python /tmp/accept.py", 900)
                world["post_failing"] = await run_suites(cid, case["suites"])
        except Exception as e:
            status = f"error: {type(e).__name__}: {e}"
    await _docker("rm", "-f", cid, timeout=120)

    world["patch"], world["status"] = patch, status
    config = {"agent": "pico", "harness": "ch07-minimal", "case": case["id"],
              "repeat": repeat, "world": case["instance_id"], "network": "none",
              "git_seal": "timesafe-v1", "setup_cmds": case["setup_cmds"]}
    traj = make_traj(instance_id=key, system=SYSTEM, task_text=task_text,
                     new_messages=new_msgs, exit_status=status, patch=patch,
                     spent=spent, api_calls=api_calls, config=config)
    (run_dir / "trajs").mkdir(parents=True, exist_ok=True)
    (run_dir / "world").mkdir(parents=True, exist_ok=True)
    (run_dir / "trajs" / f"{key}.traj.json").write_text(json.dumps(traj, indent=1))
    (run_dir / "world" / f"{key}.json").write_text(json.dumps(world, indent=1))
    return {"key": key, "case": case["id"], "repeat": repeat, "status": status,
            "seconds": round(time.time() - started), "api_calls": api_calls,
            "cost_usd": round(cost_usd(spent), 6),
            "accept_pre": world["accept_pre"], "accept_post": world["accept_post"],
            "newly_failing": sorted(set(world["post_failing"]) - set(world["baseline_failing"])),
            "patch_bytes": len(patch)}


async def main() -> None:
    args = [a for a in sys.argv[1:]]
    repeat = 5
    if "--repeat" in args:
        i = args.index("--repeat")
        repeat = int(args[i + 1])
        del args[i:i + 2]
    run_dir = Path(args[0]).resolve()
    only = set(args[1:])
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = json.loads((DATA / "issues" / "meta.json").read_text())
    cases = [c for c in load_cases() if not only or c["id"] in only]

    results_path = run_dir / "results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(l)["key"] for l in results_path.read_text().splitlines() if l}

    todo = [(c, r) for c in cases for r in range(1, repeat + 1)
            if f"{c['id']}-r{r}" not in done]
    log_file = (run_dir / "log.txt").open("a")

    def log(msg: str) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        log_file.write(line + "\n")
        log_file.flush()

    log(f"harness run: {len(todo)} to do ({len(cases)} cases x {repeat}), {len(done)} done")
    sem = asyncio.Semaphore(CONCURRENCY)
    finished = 0

    async def one(case, r):
        nonlocal finished
        async with sem:
            key = f"{case['id']}-r{r}"
            log(f"start {key} [{case['instance_id']}]")
            try:
                row = await asyncio.wait_for(
                    run_one(case, r, run_dir, meta[case["id"]]["base_commit"]), WALL_CLOCK)
            except (TimeoutError, asyncio.TimeoutError):
                await _docker("rm", "-f", f"pico-h7-{key}", timeout=120)
                row = {"key": key, "case": case["id"], "repeat": r,
                       "status": f"wall clock: no finish in {WALL_CLOCK}s"}
            with results_path.open("a") as f:
                f.write(json.dumps(row) + "\n")
            finished += 1
            log(f"done {key} [{finished}/{len(todo)}] {row['status']} "
                f"{row.get('seconds', '?')}s accept_post={row.get('accept_post')}")

    await asyncio.gather(*(one(c, r) for c, r in todo))
    log("run complete")


if __name__ == "__main__":
    asyncio.run(main())
