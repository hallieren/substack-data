"""Pre-flight, zero model calls: every accept script must exit 1 (red, probe
ran) on its unfixed world, and every declared suite must run and parse.
Catches broken probes before any agent money is spent. Also proves "reset":
builds the world twice and compares the /testbed content hash.

Usage: cd ~/Documents/pico && uv run python <here>/verify_accept.py [case_id ...]
"""

import asyncio
import json
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
sys.path[:0] = [str(HARNESS), str(Path.home() / "Documents/pico/bench")]

from swebench_mini import _docker, image, seal_git  # noqa: E402

from cases import load_cases  # noqa: E402
from runner import parse_failures, push_file, sh  # noqa: E402

CONCURRENCY = 4
HASH_CMD = ("find /testbed -type f -not -path '*/.git/*' -print0 | sort -z | "
            "xargs -0 sha256sum | sha256sum")


async def boot(case, meta, tag):
    cid = f"pico-h7v-{case['id']}-{tag}"
    await _docker("rm", "-f", cid, timeout=60)
    img = image(case["instance_id"])
    code, out = await _docker("run", "-d", "--network", "none", "--name", cid, img,
                              "tail", "-f", "/dev/null", timeout=3600)
    if code != 0:
        img = img.replace(".arm64.", ".x86_64.")
        code, out = await _docker("run", "-d", "--network", "none",
                                  "--platform", "linux/amd64", "--name", cid, img,
                                  "tail", "-f", "/dev/null", timeout=3600)
    if code != 0:
        return None, f"container failed: {out.strip()[:150]}"
    sc, so = await seal_git(cid, meta[case["id"]]["base_commit"])
    if sc != 0:
        await _docker("rm", "-f", cid, timeout=60)
        return None, f"seal failed: {so.strip()[:150]}"
    return cid, "ok"


async def verify(case, meta, results):
    row = {"case": case["id"], "world": case["instance_id"]}
    cid, msg = await boot(case, meta, "a")
    if not cid:
        row["error"] = msg
        results.append(row)
        print(json.dumps(row))
        return
    try:
        for cmd in case["setup_cmds"]:
            sc, so = await sh(cid, cmd, 120)
            row.setdefault("setup", []).append(f"{cmd} -> {sc}")
        # hash BEFORE any probe runs: the reset claim is about the start state
        _, h1 = await sh(cid, HASH_CMD, 600)
        await push_file(cid, "/tmp/accept.py", case["accept_py"])
        code, out = await sh(cid, "python /tmp/accept.py", 900)
        row["accept_pre"] = code
        row["accept_out"] = out.strip()[-600:]
        if case["suites"]:
            sc, sout = await sh(cid, case["suites"]["cmd"], 1800)
            row["suites_exit"] = sc
            row["suites_failing"] = parse_failures(case["suites"]["parser"], sout)
            row["suites_tail"] = sout.strip()[-300:]
    finally:
        await _docker("rm", "-f", cid, timeout=120)
    # reset proof: a second world, same hash
    cid2, msg2 = await boot(case, meta, "b")
    if cid2:
        try:
            for cmd in case["setup_cmds"]:
                await sh(cid2, cmd, 120)
            _, h2 = await sh(cid2, HASH_CMD, 600)
            row["reset_identical"] = h1.strip() == h2.strip()
            row["world_hash"] = h1.strip().split()[0][:24]
        finally:
            await _docker("rm", "-f", cid2, timeout=120)
    results.append(row)
    print(json.dumps({k: v for k, v in row.items() if k != "accept_out"}))


async def main():
    only = set(sys.argv[1:])
    meta = json.loads((HARNESS.parent / "issues" / "meta.json").read_text())
    cases = [c for c in load_cases() if not only or c["id"] in only]
    results = []
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(c):
        async with sem:
            await verify(c, meta, results)

    await asyncio.gather(*(one(c) for c in cases))
    out = HARNESS.parent / "runs" / "verify-accept.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(sorted(results, key=lambda r: r["case"]), indent=1))
    bad = [r for r in results if r.get("accept_pre") != 1 or "error" in r]
    print(f"\n{len(results)} verified, {len(bad)} need attention: "
          + ", ".join(r["case"] for r in bad))


if __name__ == "__main__":
    asyncio.run(main())
