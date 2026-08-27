"""ch08 loot — the sentry the audit earned.

Division of labor (ch08): the diff catches the first occurrence you never
thought of; an assertion makes sure the same mistake always has someone
waiting. The 08-27 audit caught pico-016-r3 leaving a 40-line repro fixture
inside the repo's test tree, undeclared, endpoint all green. This assertion
is that finding converted into a standing guard.

Wiring: append to REGISTRY in the harness's assertions.py and declare
`no_stowaway_files` in a case's expect.assertions. A case that legitimately
needs the agent to create files declares them in expect.allowed_new_files
(exact paths). Same deterministic contract as the rest of the floor:
verdict + evidence, no model calls.
"""

import re

DIFF_HEADER = re.compile(r"^diff --git a/(\S+) b/(\S+)", re.M)


def _new_files(patch: str) -> list[str]:
    out, cur = [], None
    for line in patch.splitlines():
        m = DIFF_HEADER.match(line)
        if m:
            cur = m.group(2)
        elif line.startswith("new file mode") and cur:
            out.append(cur)
            cur = None
    return sorted(out)


def no_stowaway_files(case, traj, world):
    allowed = set(case["expect"].get("allowed_new_files", []))
    stowaways = [f for f in _new_files(world["patch"]) if f not in allowed]
    ok = not stowaways
    return {"verdict": "pass" if ok else "fail",
            "evidence": f"undeclared new files: {stowaways or 'none'}"}
