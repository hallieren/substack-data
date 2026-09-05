"""Build one docker image per case (cases/<id>/meta.json -> pico-world:<id>).

Zero model calls. Failures are logged to worlds/build.jsonl with the tail of
the build output; a case whose world does not build is excluded, never faked.

Usage: python build_worlds.py [case_id ...]
"""
import json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).parent
CASES = HERE / "cases"
LOG = HERE / "worlds" / "build.jsonl"

INSTALL = {
    "sympy/sympy": "pip install -q -e . && pip install -q pytest hypothesis numpy lark z3-solver",
    "pylint-dev/pylint": "pip install -q -r requirements_test_min.txt",
    "pydata/xarray": "pip install -q -e . && pip install -q pytest hypothesis 'numpy<2.4' pandas pytest-mypy-plugins pytest-timeout pytest-xdist pytest-asyncio",
    "pallets/flask": "pip install -q -e . && pip install -q pytest",
    "mwaskom/seaborn": "pip install -q -e .[stats] && pip install -q pytest",
}


def build(meta: dict) -> dict:
    t = time.time()
    cmd = ["docker", "build", "-q", "-f", str(HERE / "worlds" / "Dockerfile"),
           "--build-arg", f"REPO={meta['repo']}", "--build-arg", f"SHA={meta['base_sha']}",
           "--build-arg", f"INSTALL={INSTALL[meta['repo']]}",
           "-t", meta["image"], str(HERE / "worlds")]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"id": meta["id"], "ok": p.returncode == 0, "seconds": round(time.time() - t),
            "tail": (p.stdout + p.stderr).strip()[-600:]}


def main():
    only = set(sys.argv[1:])
    metas = [json.loads((d / "meta.json").read_text()) for d in sorted(CASES.iterdir())
             if (d / "meta.json").exists()]
    metas = [m for m in metas if not only or m["id"] in only]
    for m in metas:
        r = build(m)
        with LOG.open("a") as f:
            f.write(json.dumps(r) + "\n")
        print(f"{m['id']}: {'ok' if r['ok'] else 'FAIL'} {r['seconds']}s"
              + ("" if r["ok"] else "\n  " + r["tail"][-300:]), flush=True)


if __name__ == "__main__":
    main()
