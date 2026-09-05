"""reference — the human's merged fix as the replay rung's reference answer.

ch13 replay policy (differs from ch07's P1): the tests the maintainers merged
alongside the fix are the verdict source. FAIL_TO_PASS = tests that fail on
the base commit with the PR's test changes applied and pass once the human's
source change is applied too; PASS_TO_PASS = pass in both states. pico never
sees either patch: the container is sealed at the base commit, network off,
and the test patch is applied only after pico's run ends.

Everything here is deterministic given container output. No model calls.
"""
import re
from pathlib import Path

RESULT = re.compile(r"^(PASSED|FAILED|ERROR|XFAIL|XPASS)\s+(\S+::\S+)", re.M)
PYTEST = "python -m pytest -rA -q -p no:cacheprovider --continue-on-collection-errors"


def suite_commands(repo: str, test_files: list[str], existing: set[str]) -> list[str]:
    """One or more pytest invocations covering the PR's test files.

    pylint's functional tests are data files driven by tests/test_functional.py,
    so they are selected with -k on the stem instead of run directly."""
    direct, stems = [], []
    for p in test_files:
        if repo == "pylint-dev/pylint" and p.startswith("tests/functional/"):
            if p.endswith(".py"):
                stems.append(Path(p).stem)
        elif p.endswith(".py") and re.search(r"(^|/)test_[^/]+\.py$|_test\.py$", p):
            if p in existing:
                direct.append(p)
    cmds = []
    # xarray's pyproject addopts pin mypy-plugin flags that differ across
    # commits; the plugin is irrelevant to the reference tests, drop addopts.
    py = PYTEST + (' -o addopts=""' if repo == "pydata/xarray" else "")
    if direct:
        cmds.append(f"{py} {' '.join(direct)}")
    if stems:
        cmds.append(f"{PYTEST} tests/test_functional.py -k \"{' or '.join(stems)}\"")
    return cmds


def parse_results(output: str) -> dict[str, str]:
    out = {}
    for m in RESULT.finditer(output):
        out[m.group(2)] = m.group(1)
    return out


def failing(results: dict[str, str]) -> list[str]:
    return sorted(k for k, v in results.items() if v in ("FAILED", "ERROR"))


def fail_to_pass(pre: dict, post: dict) -> list[str]:
    return sorted(k for k, v in pre.items() if v in ("FAILED", "ERROR") and post.get(k) == "PASSED")


def pass_to_pass(pre: dict, post: dict) -> list[str]:
    return sorted(k for k, v in pre.items() if v == "PASSED" and post.get(k) == "PASSED")
