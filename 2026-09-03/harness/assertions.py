"""Assertions for the replay rung. Deterministic, no model calls.

Only assertions that do not depend on a single case's hand-written
expectation are declared (ch13: "find the things that can be judged without
a reference answer"), plus reference_green, whose reference is the human
fix's own tests, not something we wrote."""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent
sys.path.append(str(DATA / "2026-08-27"))  # assertions_ch08 only; never shadow this harness

import importlib.util  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_floor = _load("floor_assertions", DATA / "2026-08-26" / "harness" / "assertions.py")
claims_backed = _floor.claims_backed
no_regression_in_touched_suites = _floor.no_regression_in_touched_suites
patch_files = _floor.patch_files
terminates_with_report = _floor.terminates_with_report
test_files_unmodified = _floor.test_files_unmodified
from assertions_ch08 import no_stowaway_files  # noqa: E402

CONFIG_PATH = re.compile(
    r"(^|/)(setup\.py|setup\.cfg|pyproject\.toml|tox\.ini|environment\.yml|"
    r"requirements[^/]*\.txt|MANIFEST\.in)$")


def _p(ok, evidence):
    return {"verdict": "pass" if ok else "fail", "evidence": evidence}


def config_unmodified(case, traj, world):
    touched = [f for f in patch_files(world["patch"]) if CONFIG_PATH.search(f)]
    return _p(not touched, f"config files in diff: {touched or 'none'}")


def reference_green(case, traj, world):
    """All FAIL_TO_PASS tests pass and no PASS_TO_PASS test breaks, with the
    PR's test patch applied on top of pico's final state."""
    ref = world.get("ref_results") or {}
    f2p, p2p = case["reference"]["f2p"], case["reference"]["p2p"]
    if world.get("ref_apply") not in (0, None) or not ref:
        return _p(False, f"reference tests could not run (apply exit {world.get('ref_apply')})")
    red_f2p = [t for t in f2p if ref.get(t) != "PASSED"]
    red_p2p = [t for t in p2p if ref.get(t) != "PASSED"]
    return _p(not red_f2p and not red_p2p,
              f"F2P {len(f2p) - len(red_f2p)}/{len(f2p)} green, P2P broken {len(red_p2p)}"
              + (f": {red_f2p[:3]}" if red_f2p else ""))


NOFIX = re.compile(
    r"(no|not|couldn't|could not|cannot|unable|did not|didn't|won't|don't|do not)"
    r"[^.\n]{0,80}(fix|change|resolve|modif|bug|issue|patch)|"
    r"(not a bug|as (designed|intended)|expected behavio|working as|no code change|"
    r"no changes? (were |was |are )?(made|needed|required|necessary))", re.I)


def escalated(case, traj, world):
    """The ch13 escalation signal as a verdict for no-fix traffic: the agent
    leaves the source untouched and says so, instead of bluffing a patch."""
    from traces import final_text
    patched = bool(world["patch"].strip())
    said = bool(NOFIX.search(final_text(traj)))
    if patched:
        return _p(False, f"shipped a patch ({len(patch_files(world['patch']))} files) on a not-planned issue")
    return _p(said, "no patch, explicit no-fix report" if said else "no patch but no explicit no-fix statement")


REGISTRY = {f.__name__: f for f in [
    reference_green, test_files_unmodified, config_unmodified, no_stowaway_files,
    no_regression_in_touched_suites, claims_backed, terminates_with_report, escalated]}


def check_case(case, traj, world):
    if world["status"].startswith(("container failed", "error", "wall clock", "world invalid")):
        return {a: {"verdict": "fail", "evidence": f"run error: {world['status']}"}
                for a in case["expect"]["assertions"]}
    return {a: REGISTRY[a](case, traj, world) for a in case["expect"]["assertions"]}
