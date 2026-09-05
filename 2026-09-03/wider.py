"""Register row 2 evidence: does a pass on the PR's own test files hide a
regression in the wider suite? For every replay run that passed
reference_green, rebuild the world, run the whole test directory that holds
the PR's test files (baseline), apply pico's patch, run it again, and list
newly failing tests. Zero model calls, CPU only.

Writes analysis/wider.json + analysis/wider.md.
Usage: cd ~/Documents/pico && uv run python wider.py [runs/replay]
"""
import asyncio, json, sys, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path[:0] = [str(HERE / "harness"), str(Path.home() / "Documents/pico/bench")]
from reference import PYTEST, parse_results, failing  # noqa: E402
from swebench_mini import _docker  # noqa: E402

CONCURRENCY = 3
SUITE_TIMEOUT = 2400


async def sh(cid, command, timeout=SUITE_TIMEOUT):
    wrapped = f"source /opt/miniconda3/bin/activate testbed && cd /testbed && {{ {command}\n}}"
    try:
        return await _docker("exec", cid, "bash", "-c", wrapped, timeout=timeout)
    except TimeoutError:
        return 124, f"killed: no completion within {timeout}s"


async def push(cid, path, content):
    await _docker("exec", "-i", cid, "bash", "-c", f"cat > {path}", stdin=content.encode(), timeout=60)


def wider_target(meta):
    dirs = sorted({str(Path(p).parent) for p in meta["test_files"] if p.endswith(".py")})
    if meta["repo"] == "pylint-dev/pylint":
        return ["tests/test_functional.py", "tests/checkers"] if any(d.startswith("tests/functional") for d in dirs) else dirs
    return dirs


async def one(meta, world, sem):
    async with sem:
        cid = f"pico-w-{meta['id']}"
        t = time.time()
        rec = {"id": meta["id"], "target": wider_target(meta)}
        await _docker("rm", "-f", cid, timeout=60)
        await _docker("run", "-d", "--network", "none", "--name", cid, meta["image"], "tail", "-f", "/dev/null", timeout=600)
        try:
            py = PYTEST + (' -o addopts=""' if meta["repo"] == "pydata/xarray" else "")
            cmd = f"{py} {' '.join(rec['target'])}"
            _, out = await sh(cid, cmd)
            base = parse_results(out)
            await push(cid, "/tmp/pico.patch", world["patch"])
            code, aout = await sh(cid, "git apply --whitespace=nowarn /tmp/pico.patch || git apply --ignore-whitespace --whitespace=nowarn /tmp/pico.patch", 120)
            if code != 0:
                rec["error"] = f"pico patch did not apply: {aout[-200:]}"
            else:
                _, out2 = await sh(cid, cmd)
                post = parse_results(out2)
                rec["n_base"], rec["n_post"] = len(base), len(post)
                rec["baseline_failing"] = failing(base)
                rec["newly_failing"] = sorted(set(failing(post)) - set(failing(base)))
                rec["vanished"] = sorted(set(base) - set(post))
        finally:
            rec["seconds"] = round(time.time() - t)
            await _docker("rm", "-f", cid, timeout=120)
        print(f"{meta['id']}: n={rec.get('n_base')} newly_failing={len(rec.get('newly_failing', []))} "
              f"{rec.get('error', '')} {rec['seconds']}s", flush=True)
        return rec


async def main(run_dir):
    run_dir = Path(run_dir)
    results = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l]
    passed = [r for r in results if r.get("f2p_total") and r["f2p_green"] == r["f2p_total"] and r["status"] == "done"]
    sem = asyncio.Semaphore(CONCURRENCY)
    jobs = []
    for r in passed:
        meta = json.loads((HERE / "cases" / r["case"] / "meta.json").read_text())
        world = json.loads((run_dir / "world" / f"{r['key']}.json").read_text())
        jobs.append(one(meta, world, sem))
    recs = await asyncio.gather(*jobs)
    (HERE / "analysis" / "wider.json").write_text(json.dumps(recs, indent=1))
    L = ["# Wider suite on every reference-green run (register row 2)", "",
         "| case | wider target | tests | newly failing after pico's patch |", "|---|---|---|---|"]
    for rec in recs:
        L.append(f"| {rec['id']} | {' '.join(rec['target'])} | {rec.get('n_base', '?')} | "
                 f"{rec.get('error') or (', '.join(rec.get('newly_failing', [])) or 'none')} |")
    (HERE / "analysis" / "wider.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else HERE / "runs" / "replay"))
