"""Pre-flight every world (the ch07 verify_accept.py of this run, zero model calls).

Per case, in a fresh --network none container of pico-world:<id>:
  1. baseline: run the PR's test files as they exist at the base commit
     (feeds no_regression_in_touched_suites later)
  2. apply test.patch  -> run -> ref_pre   (must contain >= 1 failure)
  3. apply fix.patch   -> run -> ref_post  (FAIL_TO_PASS = pre red, post green)
A world with no FAIL_TO_PASS, or whose patches do not apply, is invalid and
excluded, never scored. Writes cases/<id>/reference.json.

Usage: python verify_worlds.py [case_id ...]
"""
import asyncio, json, sys, time
from pathlib import Path

HERE = Path(__file__).parent
sys.path[:0] = [str(HERE / "harness"), str(Path.home() / "Documents/pico/bench")]
from reference import suite_commands, parse_results, failing, fail_to_pass, pass_to_pass  # noqa
from swebench_mini import _docker  # noqa

CASES = HERE / "cases"
CONCURRENCY = 4


async def sh(cid, command, timeout=1500):
    wrapped = f"source /opt/miniconda3/bin/activate testbed && cd /testbed && {{ {command}\n}}"
    try:
        return await _docker("exec", cid, "bash", "-c", wrapped, timeout=timeout)
    except TimeoutError:
        return 124, f"killed: no completion within {timeout}s"


async def push(cid, path, content):
    code, out = await _docker("exec", "-i", cid, "bash", "-c", f"cat > {path}",
                              stdin=content.encode(), timeout=60)
    if code != 0:
        raise RuntimeError(f"push {path}: {out[:200]}")


async def existing(cid, paths):
    code, out = await sh(cid, "for p in " + " ".join(f"'{p}'" for p in paths) + "; do [ -e \"$p\" ] && echo \"$p\"; done; true")
    return set(out.split())


async def run_suites(cid, meta):
    ex = await existing(cid, meta["test_files"])
    results, cmds = {}, suite_commands(meta["repo"], meta["test_files"], ex)
    for c in cmds:
        _, out = await sh(cid, c)
        results.update(parse_results(out))
    return results, cmds


async def verify(meta):
    cid = f"pico-v-{meta['id']}"
    d = CASES / meta["id"]
    t = time.time()
    rec = {"id": meta["id"], "valid": False, "reason": "", "baseline_failing": [],
           "ref_pre_failing": [], "f2p": [], "p2p": [], "post_failing_with_fix": [], "cmds": []}
    await _docker("rm", "-f", cid, timeout=60)
    code, out = await _docker("run", "-d", "--network", "none", "--name", cid, meta["image"],
                              "tail", "-f", "/dev/null", timeout=600)
    try:
        if code != 0:
            rec["reason"] = f"container: {out[:200]}"; return rec
        base, _ = await run_suites(cid, meta)
        rec["baseline_failing"] = failing(base)
        await push(cid, "/tmp/test.patch", (d / "test.patch").read_text())
        await push(cid, "/tmp/fix.patch", (d / "fix.patch").read_text())
        code, out = await sh(cid, "git apply --whitespace=nowarn /tmp/test.patch || git apply --ignore-whitespace --whitespace=nowarn /tmp/test.patch")
        if code != 0:
            rec["reason"] = f"test.patch does not apply: {out[-200:]}"; return rec
        pre, cmds = await run_suites(cid, meta)
        rec["cmds"] = cmds
        rec["ref_pre_failing"] = failing(pre)
        code, out = await sh(cid, "git apply --whitespace=nowarn /tmp/fix.patch || git apply --ignore-whitespace --whitespace=nowarn /tmp/fix.patch")
        if code != 0:
            rec["reason"] = f"fix.patch does not apply: {out[-200:]}"; return rec
        post, _ = await run_suites(cid, meta)
        rec["f2p"] = fail_to_pass(pre, post)
        rec["p2p"] = pass_to_pass(pre, post)
        rec["post_failing_with_fix"] = failing(post)
        rec["n_pre"], rec["n_post"] = len(pre), len(post)
        if not pre:
            rec["reason"] = "no test results parsed (suite did not run)"
        elif not rec["f2p"]:
            rec["reason"] = "no FAIL_TO_PASS: the PR's tests do not go red->green here"
        else:
            rec["valid"] = True
        return rec
    finally:
        rec["seconds"] = round(time.time() - t)
        await _docker("rm", "-f", cid, timeout=120)
        (d / "reference.json").write_text(json.dumps(rec, indent=1))


async def main():
    only = set(sys.argv[1:])
    metas = [json.loads((d / "meta.json").read_text()) for d in sorted(CASES.iterdir())
             if (d / "meta.json").exists()]
    metas = [m for m in metas if not only or m["id"] in only]
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(m):
        async with sem:
            r = await verify(m)
            print(f"{m['id']}: {'valid' if r['valid'] else 'INVALID'} f2p={len(r['f2p'])} "
                  f"p2p={len(r['p2p'])} base_fail={len(r['baseline_failing'])} "
                  f"post_fail={len(r['post_failing_with_fix'])} {r.get('seconds')}s {r['reason']}", flush=True)
    await asyncio.gather(*(one(m) for m in metas))


if __name__ == "__main__":
    asyncio.run(main())
