#!/usr/bin/env python
"""Acceptance probe for pico-012 (world: pylint-dev__pylint-4970).

Verdict source (policy P1): issues/pico-012.md ONLY.

  "Setting `min-similarity-lines` to `0` in the rcfile doesn't disable checking
   for duplicate code, it instead treats every line of code as duplicate and
   raises many errors."
  "Setting `min-similarity-lines` to `0` should disable the duplicate code
   check.  It works that way in many other linters (like flake8).  Setting a
   numerical value in flake8 to `0` (e.g. `max-line-length`) disables that
   check."

The issue asks for a *disable switch*, not merely for silence.  So this probe
checks both halves of that sentence:

  probe 0 (control / fixture self-check) -- with min-similarity-lines=4 the
      fixture MUST produce duplicate-code, and duplicate-code MUST report as an
      enabled check.  Otherwise the probe is measuring nothing -> exit 2.
  probe 1 (no messages) -- with min-similarity-lines=0, pylint emits NO
      duplicate-code (R0801) message and does not blow up.  This is the issue's
      "current problem" (a flood of duplicate-code errors) turned into an
      assertion.
  probe 2 (the check is off) -- with min-similarity-lines=0, the duplicate code
      check must actually be DISABLED, not merely silent by arithmetic
      accident.  Accepted evidence, any one of:
        (a) duplicate-code reports as a disabled message on the linter, or
        (b) the similarities checker is dropped from the prepared checkers, or
        (c) the similarities checker scanned nothing (collected no linesets)
            during a run over files that are full of duplicated code.
      A `0` that leaves the check registered, enabled and scanning is the
      "doesn't disable checking for duplicate code" the issue reports.

Exit codes: 0 acceptance met - 1 acceptance not met - 2 probe broken.
"""

import json
import os
import subprocess
import sys
import tempfile
import traceback

# 12 identical lines, well above pylint's default min-similarity-lines (4).
DUPLICATED_BLOCK = """\
    running_total = 0
    for element in elements:
        running_total += element
        running_total *= 2
        running_total -= 1
        running_total += 3
        running_total //= 1
        running_total += 7
        running_total -= 2
        running_total *= 1
        running_total += 11
    return running_total
"""

MODULE_TEMPLATE = '''\
"""Module {name} for the pico-012 duplicate-code fixture."""


def {name}_entry(elements):
    """Do arithmetic on ``elements``."""
{block}
'''

RCFILE_TEMPLATE = """\
[MASTER]
persistent=no

[SIMILARITIES]
min-similarity-lines={value}
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=no
"""

# Runs pylint in-process so we can look at the linter's own view of whether the
# duplicate code check is on.  Kept in a child process so that a blow-up here
# cannot take accept.py with it.
INSPECT_SRC = r'''
import json
import sys

from pylint.lint import Run

rcfile = sys.argv[1]
targets = sys.argv[2:]
argv = ["--rcfile", rcfile] + targets

try:
    run = Run(argv, exit=False)
except TypeError:
    run = Run(argv, do_exit=False)

linter = run.linter

similarities = None
for checker in linter.get_checkers():
    if getattr(checker, "name", None) == "similarities":
        similarities = checker
        break

try:
    prepared = [getattr(c, "name", "") for c in linter.prepare_checkers()]
except Exception:
    prepared = None

info = {
    "message_enabled": bool(linter.is_message_enabled("duplicate-code")),
    "checker_registered": similarities is not None,
    "min_lines": getattr(similarities, "min_lines", None),
    "linesets": (
        len(getattr(similarities, "linesets", None) or [])
        if similarities is not None
        else None
    ),
    "checker_prepared": (
        None if prepared is None else ("similarities" in prepared)
    ),
}
sys.stderr.write("PICO012_JSON " + json.dumps(info) + "\n")
'''

DUP_SYMBOL = "duplicate-code"
DUP_MSGID = "R0801"
MARKER = "PICO012_JSON "


def write_fixture(workdir):
    """Three modules sharing one identical 12-line block."""
    names = []
    for name in ("alpha", "beta", "gamma"):
        with open(os.path.join(workdir, name + ".py"), "w") as handle:
            handle.write(MODULE_TEMPLATE.format(name=name, block=DUPLICATED_BLOCK))
        names.append(name + ".py")
    return names


def write_rcfile(workdir, value):
    path = os.path.join(workdir, "pylintrc_min%s" % value)
    with open(path, "w") as handle:
        handle.write(RCFILE_TEMPLATE.format(value=value))
    return path


def child_env(workdir):
    env = dict(os.environ)
    # keep pylint away from the real HOME / stats cache
    env["HOME"] = workdir
    env["PYLINTHOME"] = os.path.join(workdir, ".pylint.d")
    return env


def run_cmd(cmd, workdir):
    proc = subprocess.Popen(
        cmd,
        cwd=workdir,
        env=child_env(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    out, err = proc.communicate(timeout=600)
    return proc.returncode, out, err


def run_pylint_json(workdir, rcfile, targets):
    cmd = [
        sys.executable,
        "-m",
        "pylint",
        "--rcfile",
        rcfile,
        "--output-format=json",
    ] + targets
    return run_cmd(cmd, workdir)


def run_inspect(workdir, rcfile, targets):
    script = os.path.join(workdir, "_pico012_inspect.py")
    if not os.path.exists(script):
        with open(script, "w") as handle:
            handle.write(INSPECT_SRC)
    rc, out, err = run_cmd(
        [sys.executable, script, rcfile] + targets, workdir
    )
    info = None
    for line in (err or "").splitlines():
        if line.startswith(MARKER):
            try:
                info = json.loads(line[len(MARKER):])
            except ValueError:
                info = None
            break
    return rc, out, err, info


def parse_messages(stdout):
    """List of pylint json messages, or None when stdout is not pylint json."""
    text = (stdout or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, list):
        return None
    return [m for m in data if isinstance(m, dict)]


def msg_id_of(message):
    for key in ("message-id", "messageId", "message_id"):
        if key in message:
            return str(message[key])
    return ""


def duplicate_messages(messages):
    return [
        m
        for m in messages
        if str(m.get("symbol", "")) == DUP_SYMBOL
        or msg_id_of(m).upper() == DUP_MSGID
    ]


def fatal_messages(messages):
    return [
        m
        for m in messages
        if str(m.get("type", "")).lower() == "fatal"
        or msg_id_of(m).upper().startswith("F")
    ]


def main():
    workdir = tempfile.mkdtemp(prefix="pico012_")
    targets = write_fixture(workdir)
    rc_on = write_rcfile(workdir, 4)
    rc_off = write_rcfile(workdir, 0)

    # ---------------------------------------------------------------- probe 0
    code4, out4, err4 = run_pylint_json(workdir, rc_on, targets)
    msgs4 = parse_messages(out4)
    if msgs4 is None:
        print(
            "probe 0 (control, min-similarity-lines=4): BROKEN - pylint did not "
            "emit parseable json (rc=%d); stdout[:300]=%r stderr[:300]=%r"
            % (code4, (out4 or "")[:300], (err4 or "")[:300])
        )
        return 2
    dup4 = duplicate_messages(msgs4)
    if not dup4:
        print(
            "probe 0 (control, min-similarity-lines=4): BROKEN - a fixture of 3 "
            "modules sharing an identical 12-line block produced NO "
            "duplicate-code message (rc=%d, %d messages); the similarity checker "
            "is not being exercised, so nothing here can judge the issue. "
            "stderr[:300]=%r" % (code4, len(msgs4), (err4 or "")[:300])
        )
        return 2

    rci4, outi4, erri4, info4 = run_inspect(workdir, rc_on, targets)
    if info4 is None:
        print(
            "probe 0 (control, min-similarity-lines=4): BROKEN - could not read "
            "the linter's view of the duplicate-code check (rc=%d); "
            "stderr[-400:]=%r" % (rci4, (erri4 or "")[-400:])
        )
        return 2
    if not info4.get("message_enabled") or not info4.get("linesets"):
        print(
            "probe 0 (control, min-similarity-lines=4): BROKEN - baseline state "
            "is not what this probe assumes: message_enabled=%r linesets=%r "
            "checker_prepared=%r min_lines=%r. Cannot tell 'disabled' from "
            "'never on'."
            % (
                info4.get("message_enabled"),
                info4.get("linesets"),
                info4.get("checker_prepared"),
                info4.get("min_lines"),
            )
        )
        return 2

    print(
        "probe 0 (control, min-similarity-lines=4): OK - fixture %s produced %d "
        "duplicate-code (R0801) message(s) (rc=%d); linter reports "
        "duplicate-code enabled=%r, similarities checker scanned %d lineset(s), "
        "min_lines=%r."
        % (
            targets,
            len(dup4),
            code4,
            info4.get("message_enabled"),
            info4.get("linesets"),
            info4.get("min_lines"),
        )
    )

    # ---------------------------------------------------------------- probe 1
    code0, out0, err0 = run_pylint_json(workdir, rc_off, targets)
    msgs0 = parse_messages(out0)

    broke = []
    if msgs0 is None:
        broke.append("stdout is not parseable pylint json")
    if code0 & 1:
        broke.append("exit code %d has pylint's FATAL bit set" % code0)
    if code0 == 32:
        broke.append("exit code 32 (usage error): pylint rejected the config")
    if "Traceback (most recent call last)" in (err0 or ""):
        broke.append("traceback on stderr")
    if msgs0 is not None and fatal_messages(msgs0):
        broke.append(
            "fatal message(s): %s"
            % ", ".join(
                sorted(
                    {
                        str(m.get("symbol") or msg_id_of(m))
                        for m in fatal_messages(msgs0)
                    }
                )
            )
        )

    if broke:
        print(
            "probe 1 (min-similarity-lines=0 emits nothing): FAIL - pylint did "
            "not run cleanly with min-similarity-lines=0: %s. rc=%d "
            "stdout[:300]=%r stderr[:300]=%r"
            % ("; ".join(broke), code0, (out0 or "")[:300], (err0 or "")[:300])
        )
        return 1

    dup0 = duplicate_messages(msgs0)
    if dup0:
        sample = dup0[0]
        print(
            "probe 1 (min-similarity-lines=0 emits nothing): FAIL - expected the "
            "duplicate code check to be disabled, but pylint emitted %d "
            "duplicate-code (R0801) message(s) on %s (rc=%d). First: %s:%s %s"
            % (
                len(dup0),
                targets,
                code0,
                sample.get("path"),
                sample.get("line"),
                str(sample.get("message", ""))[:160].replace("\n", " | "),
            )
        )
        return 1

    print(
        "probe 1 (min-similarity-lines=0 emits nothing): PASS - pylint ran "
        "cleanly (rc=%d, %d message(s), none fatal) and emitted 0 duplicate-code "
        "(R0801) messages on the same fixture that yielded %d at "
        "min-similarity-lines=4." % (code0, len(msgs0), len(dup4))
    )

    # ---------------------------------------------------------------- probe 2
    rci0, outi0, erri0, info0 = run_inspect(workdir, rc_off, targets)
    if info0 is None:
        print(
            "probe 2 (min-similarity-lines=0 disables the check): FAIL - loading "
            "a config with min-similarity-lines=0 did not survive far enough to "
            "report the check's state (rc=%d); stderr[-400:]=%r"
            % (rci0, (erri0 or "")[-400:])
        )
        return 1

    evidence = []
    if info0.get("message_enabled") is False:
        evidence.append("duplicate-code reports as a disabled message")
    if info0.get("checker_prepared") is False:
        evidence.append("the similarities checker is dropped from prepare_checkers()")
    if info0.get("linesets") == 0:
        evidence.append("the similarities checker collected 0 linesets (scanned nothing)")

    if not evidence:
        print(
            "probe 2 (min-similarity-lines=0 disables the check): FAIL - with "
            "min-similarity-lines=0 the duplicate code check is still on: "
            "duplicate-code enabled=%r, checker registered=%r, prepared=%r, "
            "linesets scanned=%r, min_lines=%r. The issue asks for `0` to "
            "disable the check (as `0` does in flake8), not merely to make it "
            "find nothing."
            % (
                info0.get("message_enabled"),
                info0.get("checker_registered"),
                info0.get("checker_prepared"),
                info0.get("linesets"),
                info0.get("min_lines"),
            )
        )
        return 1

    print(
        "probe 2 (min-similarity-lines=0 disables the check): PASS - %s "
        "(control at min-similarity-lines=4: enabled=%r, prepared=%r, "
        "linesets=%r)."
        % (
            "; ".join(evidence),
            info4.get("message_enabled"),
            info4.get("checker_prepared"),
            info4.get("linesets"),
        )
    )
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        print("probe BROKEN: unexpected exception in accept.py (see traceback above)")
        sys.stdout.flush()
        sys.exit(2)
    sys.stdout.flush()
    sys.exit(code)
