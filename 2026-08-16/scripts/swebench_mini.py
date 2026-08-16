"""Run pico on SWE-bench Verified Mini.

Each instance runs in its official prebuilt docker container (the container is
the security boundary, so no gate). pico's four coding tools are reimplemented
over `docker exec` so the agent works on the container's filesystem and can run
the repo's tests. The patch is whatever `git diff` says when the loop stops.

Parameters mirror mini-swe-agent's swebench.yaml where they map:
max_turns=250 (their step_limit), bash timeout 60s (theirs), and a spend
ceiling standing in for their $3 cost cap.

Usage:
    PHOENIX_PROJECT_NAME=swebench-mini uv run python bench/swebench_mini.py <run_dir> [instance_id ...]

Writes to <run_dir>: preds.jsonl (official format), results.jsonl (usage,
timing, status per instance), log.txt (heartbeat). Already-finished instances
are skipped, so rerunning the same command resumes an interrupted run.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

try:
    from openinference.instrumentation import using_attributes
except ImportError:  # trace extra not installed; stamping is best-effort
    from contextlib import nullcontext

    def using_attributes(**_kw):
        return nullcontext()

from pico import session
from pico.coding import _clip, numbered
from pico.loop import Stopped, run
from pico.providers import build_provider
from pico.tools import tool
from pico.types import Usage, user

MAX_TURNS = 250
MAX_SPEND_TOKENS = 8_000_000  # ~ mini-swe-agent's $3 safety cap at V4-Flash prices
INSTANCE_WALL_CLOCK = 2400  # hard stop per instance; a hung instance must not hang the run
CONCURRENCY = 6

SYSTEM = """You are a software engineer fixing a real GitHub issue in the repository at /testbed.

Work methodically: read the relevant code before editing it, reproduce the issue
with a small script or command first, make the smallest change that fixes the
cause, then rerun your reproduction to verify. Also think about edge cases.

Rules:
- Do not modify test files or configuration; fix the source.
- Keep scratch work in /tmp. Delete any reproduction or helper files you
  created under /testbed before you finish; they would pollute the submitted diff.
- Prefer edit_file over write_file so changes stay small.
- When you are done, summarize what you changed and why. Your final state of
  /testbed will be submitted automatically as a git diff; there is no submit
  command."""

TASK = """<pr_description>
{problem_statement}
</pr_description>

I've uploaded a python code repository in /testbed. Can you help me implement
the necessary changes to the repository so that the requirements specified in
the <pr_description> are met? Make minimal changes to non-test files in
/testbed to fix the issue. The environment (dependencies, test runner) is
already set up."""


# deepseek-v4-flash-0731 pricing, USD per token
PRICE_MISS, PRICE_CACHE, PRICE_OUT = 0.14e-6, 0.0028e-6, 0.28e-6


def cost_usd(u: Usage) -> float:
    return (u.input_tokens * PRICE_MISS + u.cache_read_tokens * PRICE_CACHE
            + u.output_tokens * PRICE_OUT)


def make_traj(*, instance_id: str, system: str, task_text: str, new_messages: list,
              exit_status: str, patch: str, spent: Usage, api_calls: int,
              config: dict) -> dict:
    """The full record of one instance run, mini-swe-agent-1-shaped.

    Written from the in-memory transcript the moment the instance finishes —
    the leaderboard checklist requires trajectories generated with the
    inference process, not reconstructed afterwards."""
    messages = [{"role": "system", "content": [{"kind": "text", "text": system}]}]
    messages += [session.encode(m) for m in [user(task_text), *new_messages]]
    return {
        "trajectory_format": "pico-1",
        "instance_id": instance_id,
        "info": {
            "exit_status": exit_status,
            "submission": patch,
            "model_stats": {
                "instance_cost": round(cost_usd(spent), 6),
                "api_calls": api_calls,
                "input_tokens": spent.input_tokens,
                "cache_read_tokens": spent.cache_read_tokens,
                "output_tokens": spent.output_tokens,
            },
            "config": config,
        },
        "messages": messages,
    }


# Set once in main(); read in run_instance() so the per-request usage logger
# knows where to write. A module global keeps run_instance's signature stable.
run_dir_global: Path | None = None


def compact_at_from_env() -> int | None:
    """Compaction threshold (prompt tokens) from PICO_COMPACT_AT, or None (off)."""
    v = os.environ.get("PICO_COMPACT_AT")
    return int(v) if v else None


def make_usage_logger(run_dir: Path, instance_id: str):
    """Append one JSON line per model request: turn index + that request's usage.

    This is the Phoenix-independent record of record for the cache-vs-turn curve."""
    path = run_dir / "usage" / f"{instance_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    turn = 0

    def log(u: Usage) -> None:
        nonlocal turn
        turn += 1
        with path.open("a") as f:
            f.write(json.dumps({
                "turn": turn,
                "input_tokens": u.input_tokens,
                "output_tokens": u.output_tokens,
                "cache_read_tokens": u.cache_read_tokens,
            }) + "\n")

    return log


def image(instance_id: str) -> str:
    return f"swebench/sweb.eval.arm64.{instance_id.replace('__', '_1776_')}:latest"


# Replicates the official git_clone_timesafe sanitization (swebench main,
# image_builder/docker_utils.py) inside an already-built container. The
# prebuilt Docker Hub images (2025-04) predate the official fix and retain
# future refs — we caught the model mining them, so: keep only a branch at
# HEAD (base_commit + the image's env-setup commit, which must not be rolled
# back), drop every other ref, expire the reflog, prune unreachable objects,
# then hard-verify that at most one post-base commit (HEAD itself) survives.
GIT_SEAL = r"""
set -euo pipefail
cd /testbed
TARGET_TIMESTAMP=$(git show -s --format=%ct "$1")
git checkout -q -B pico-base
git for-each-ref --format='%(refname)' | grep -v '^refs/heads/pico-base$' \
  | while read -r ref; do git update-ref -d "$ref"; done
for rm in $(git remote); do git remote remove "$rm"; done
rm -f .git/FETCH_HEAD .git/ORIG_HEAD
git reflog expire --expire=now --all
git gc --prune=now --quiet
AFTER=$((TARGET_TIMESTAMP + 1))
FUTURE=$(git rev-list --all --after="@$AFTER" --count)
[ "$FUTURE" -le 1 ] || { echo "SEAL FAILED: $FUTURE post-base commits remain"; exit 1; }
if [ "$FUTURE" -eq 1 ]; then
  [ "$(git rev-list --all --after="@$AFTER")" = "$(git rev-parse HEAD)" ] \
    || { echo "SEAL FAILED: surviving post-base commit is not HEAD"; exit 1; }
fi
echo "sealed: $(git rev-list --all --count) commits reachable"
"""


async def seal_git(cid: str, base_commit: str) -> tuple[int, str]:
    # git gc on the big repos (django/sympy) takes minutes under emulation.
    return await _docker(
        "exec", "-i", cid, "bash", "-s", "--", base_commit,
        stdin=GIT_SEAL.encode(), timeout=900,
    )


async def _docker(
    *args: str, stdin: bytes | None = None, timeout: float = 120, merge_stderr: bool = True
) -> tuple[int, str]:
    # merge_stderr=False matters for `git diff`: the child inherits the parent's
    # gRPC/Phoenix fd, whose fork warnings land on stderr and would otherwise
    # pollute the captured patch.
    proc = await asyncio.create_subprocess_exec(
        "docker", *args,
        stdin=asyncio.subprocess.PIPE if stdin is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT if merge_stderr else asyncio.subprocess.DEVNULL,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(stdin), timeout)
    except (TimeoutError, asyncio.CancelledError):
        proc.kill()
        await proc.wait()
        raise
    return proc.returncode or 0, out.decode(errors="replace")


def container_tools(cid: str) -> list:
    """pico's four coding tools, executed inside container `cid` at /testbed."""

    async def sh(command: str, timeout: float) -> tuple[int, str]:
        # The repo's environment lives in the `testbed` conda env; a bare
        # `docker exec` lands in base, whose python has no repo dependencies.
        wrapped = f"source /opt/miniconda3/bin/activate testbed && {{ {command}\n}}"
        try:
            return await _docker(
                "exec", "-w", "/testbed", cid, "bash", "-c", wrapped, timeout=timeout
            )
        except TimeoutError:
            raise ValueError(f"killed: no completion within {timeout}s") from None

    @tool
    async def bash(command: str, timeout: int = 60) -> str:
        """Run a shell command in the repository container and return its output.

        Args:
            command: The command to run (working directory is /testbed).
            timeout: Seconds before the command is killed. Raise it for slow test suites.
        """
        code, out = await sh(command, timeout)
        return f"exit {code}\n{_clip(out)}"

    @tool
    async def read_file(path: str, offset: int = 1, limit: int = 2000) -> str:
        """Read a file and return its contents with line numbers.

        Args:
            path: Path to the file, absolute or relative to /testbed.
            offset: 1-based line number to start reading from.
            limit: Maximum number of lines to return.
        """
        code, out = await sh(f"cat -- {path!r}", 60)
        if code != 0:
            raise ValueError(out.strip())
        return numbered(out, offset, limit)

    @tool
    async def write_file(path: str, content: str) -> str:
        """Write content to a file, creating parent directories as needed.

        Args:
            path: Where to write, absolute or relative to /testbed.
            content: The full new contents of the file.
        """
        code, out = await _docker(
            "exec", "-i", "-w", "/testbed", cid, "bash", "-c",
            f'mkdir -p -- "$(dirname -- {path!r})" && cat > {path!r}',
            stdin=content.encode(), timeout=60,
        )
        if code != 0:
            raise ValueError(out.strip())
        return f"wrote {len(content)} bytes to {path}"

    @tool
    async def edit_file(path: str, old: str, new: str) -> str:
        """Replace an exact string in a file. The old string must appear exactly once.

        Args:
            path: The file to edit, absolute or relative to /testbed.
            old: The exact text to replace, including indentation.
            new: The replacement text.
        """
        code, text = await sh(f"cat -- {path!r}", 60)
        if code != 0:
            raise ValueError(text.strip())
        count = text.count(old)
        if count == 0:
            raise ValueError(f"{old!r} not found in {path}")
        if count > 1:
            raise ValueError(f"{old!r} appears {count} times in {path}; include more context")
        code, out = await _docker(
            "exec", "-i", "-w", "/testbed", cid, "bash", "-c", f"cat > {path!r}",
            stdin=text.replace(old, new).encode(), timeout=60,
        )
        if code != 0:
            raise ValueError(out.strip())
        return f"edited {path}"

    return [bash, read_file, write_file, edit_file]


async def run_instance(inst: dict) -> dict:
    iid = inst["instance_id"]
    cid = f"pico-swe-{iid.replace('__', '-')}"
    started = time.time()
    spent = Usage()

    assert run_dir_global is not None, "run_dir_global must be set by main()"
    per_request = make_usage_logger(run_dir_global, iid)

    img = image(iid)
    await _docker("rm", "-f", cid, timeout=60)
    # --network none: the container must not reach the internet. A first run
    # showed the model curl-ing the linked GitHub PR diff for some instances —
    # the leaderboard rules require safeguards against fetching solutions, and
    # a hard network boundary beats a prompt rule.
    code, out = await _docker(
        "run", "-d", "--network", "none", "--name", cid, img,
        "tail", "-f", "/dev/null", timeout=900
    )
    if code != 0:
        # Not every instance has an arm64 image (older sphinx ones don't);
        # fall back to the x86_64 image under emulation.
        img = image(iid).replace(".arm64.", ".x86_64.")
        code, out = await _docker(
            "run", "-d", "--network", "none", "--platform", "linux/amd64", "--name", cid,
            img, "tail", "-f", "/dev/null",
            timeout=1800,
        )
    if code == 0:
        # Fail closed: an unsealed container never sees the agent.
        seal_code, seal_out = await seal_git(cid, inst["base_commit"])
        if seal_code != 0:
            code, out = 1, f"git seal failed: {seal_out.strip()[:300]}"
    status, patch = "done", ""
    new_msgs: list = []
    api_calls = 0

    def count(u: Usage) -> None:
        nonlocal spent, api_calls
        spent = spent + u
        api_calls += 1
        per_request(u)

    task_text = TASK.format(problem_statement=inst["problem_statement"])
    if code != 0:
        # No container, no agent run — but the instance still gets a traj and a
        # full results row, so the run's record has no holes.
        status = f"container failed: {out.strip()[:200]}"
    else:
        try:
            provider = build_provider()
            try:
                with using_attributes(session_id=iid, metadata={"instance_id": iid}):
                    new_msgs = await run(
                        provider,
                        SYSTEM,
                        [user(task_text)],
                        container_tools(cid),
                        max_turns=MAX_TURNS,
                        max_spend_tokens=MAX_SPEND_TOKENS,
                        on_usage=count,
                        compact_at=compact_at_from_env(),
                    )
            except Stopped as e:
                status = str(e)
                new_msgs = e.messages
            # -N stages intent-to-add so files the model created show up in
            # the diff too (.gitignore still applies).
            await _docker("exec", "-w", "/testbed", cid, "git", "add", "-N", ".", timeout=120)
            _, patch = await _docker(
                "exec", "-w", "/testbed", cid, "git", "diff", timeout=120, merge_stderr=False
            )
        except Exception as e:
            status = f"error: {type(e).__name__}: {e}"
        finally:
            await _docker("rm", "-f", cid, timeout=120)
            if os.environ.get("PICO_BENCH_RMI"):
                # 500 images would swamp the disk; shared base layers survive
                # while a same-repo instance is still running.
                await _docker("rmi", img, timeout=120)

    config = {
        "agent": "pico",
        "model": os.environ.get("MODEL_NAME", ""),
        "max_turns": MAX_TURNS,
        "max_spend_tokens": MAX_SPEND_TOKENS,
        "bash_timeout_default": 60,
        "output_clip_chars": 30_000,
        "tools": ["bash", "read_file", "write_file", "edit_file"],
        "compact_at": compact_at_from_env(),
        "network": "none",
        "git_seal": "timesafe-v1",
        "submission": "git add -N . && git diff",
    }
    traj = make_traj(
        instance_id=iid, system=SYSTEM, task_text=task_text, new_messages=new_msgs,
        exit_status=status, patch=patch, spent=spent, api_calls=api_calls, config=config,
    )
    traj_path = run_dir_global / "trajs" / f"{iid}.traj.json"
    traj_path.parent.mkdir(parents=True, exist_ok=True)
    traj_path.write_text(json.dumps(traj, indent=1))

    return {
        "instance_id": iid,
        "status": status,
        "patch": patch,
        "seconds": round(time.time() - started),
        "input_tokens": spent.input_tokens,
        "cache_read_tokens": spent.cache_read_tokens,
        "output_tokens": spent.output_tokens,
        "cost_usd": round(cost_usd(spent), 6),
    }


async def main() -> None:
    global run_dir_global
    run_dir = Path(sys.argv[1])
    run_dir.mkdir(parents=True, exist_ok=True)
    run_dir_global = run_dir
    only = set(sys.argv[2:])
    instances_path = Path(os.environ.get("BENCH_INSTANCES") or Path(__file__).parent / "instances.json")
    instances = json.loads(instances_path.read_text())
    if only:
        instances = [i for i in instances if i["instance_id"] in only]

    preds_path = run_dir / "preds.jsonl"
    results_path = run_dir / "results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(l)["instance_id"] for l in results_path.read_text().splitlines() if l}
    todo = [i for i in instances if i["instance_id"] not in done]

    log_path = run_dir / "log.txt"
    log_file = log_path.open("a")

    def log(msg: str) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        log_file.write(line + "\n")
        log_file.flush()

    log(f"run start: {len(todo)} to do, {len(done)} already done")
    sem = asyncio.Semaphore(CONCURRENCY)
    finished = 0

    async def one(inst):
        nonlocal finished
        async with sem:
            iid = inst["instance_id"]
            log(f"start {iid}")
            try:
                r = await asyncio.wait_for(run_instance(inst), INSTANCE_WALL_CLOCK)
            except TimeoutError:
                await _docker("rm", "-f", f"pico-swe-{iid.replace('__', '-')}", timeout=120)
                r = {"instance_id": iid, "status": f"wall clock: no finish in {INSTANCE_WALL_CLOCK}s"}
            patch = r.pop("patch", "")
            with preds_path.open("a") as f:
                f.write(json.dumps({
                    "instance_id": iid,
                    "model_name_or_path": f"pico-{os.environ.get('MODEL_NAME', 'unknown')}",
                    "model_patch": patch,
                }) + "\n")
            with results_path.open("a") as f:
                f.write(json.dumps(r) + "\n")
            finished += 1
            tokens = r.get("input_tokens", 0) + r.get("cache_read_tokens", 0) + r.get("output_tokens", 0)
            log(f"done {iid} [{finished}/{len(todo)}] {r['status']} "
                f"{r.get('seconds', '?')}s {tokens:,} tokens patch={'yes' if patch.strip() else 'EMPTY'}")

    await asyncio.gather(*(one(i) for i in todo))
    log("run complete")


if __name__ == "__main__":
    asyncio.run(main())
