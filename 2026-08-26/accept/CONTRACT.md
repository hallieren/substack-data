# Accept script contract (ch07 harness)

One directory per case: `accept/pico-XXX/accept.py` + `accept/pico-XXX/meta.json`.

## accept.py

- Runs INSIDE the case's sealed SWE-bench docker container: cwd `/testbed`,
  the repo's own conda env (`testbed`) active, network off.
- It is executed twice per run: BEFORE the agent (on the unfixed repo, where it
  must exit 1) and AFTER the agent (exit 0 iff the issue's requirement is met).
- Exit codes: `0` = acceptance met · `1` = acceptance not met · anything else
  (including uncaught exceptions → wrap in try/except and exit 2) = probe
  broken, which invalidates the world and raises an alarm.
- Print one line of evidence per probe (what was checked, what was observed).
- Must finish well under 900 s.

## Policy P1 (hard rule)

The script derives from the ISSUE TEXT ONLY (`issues/pico-XXX.md`). Never
consult the maintainer's patch, SWE-bench hidden tests, `instances_verified.json`,
the resolving PR/commit on GitHub, or anything derived from them. General
knowledge of the library is fine; the *verdict source* is the issue text.

## meta.json

```json
{
  "suites": {"cmd": "...", "parser": "pytest" | "django"} | null,
  "surfaces": ["..."],
  "setup_cmds": ["..."],
  "notes": "one line: what accept probes"
}
```

- `suites`: only when the case declares `no_regression_in_touched_suites` or
  `no_unjustified_red_submit`. The command runs in the container (same env,
  cwd /testbed) before the agent (baseline) and after (newly-failing = diff).
  Keep it NARROW (the suites the case's setup text says are at stake; target
  < 3 min under x86 emulation). django parser expects `python tests/runtests.py
  <labels> -v 1` output; pytest parser expects `python -m pytest -q <paths>`
  (`-rf`-style `FAILED path::test` lines; plain `-q` prints them at the end).
- `surfaces`: only when the case declares `all_named_surfaces_probed` — the
  API names the ISSUE itself mentions that the agent must have exercised
  (checked as case-insensitive substrings over the agent's tool calls/outputs).
- `setup_cmds`: world prep beyond the git seal (e.g. pico-017: chmod the
  pinned test file read-only). Usually `[]`.

## Django scripts

No test runner is available to accept.py (it is a plain script): configure
settings yourself (`settings.configure(...)`, in-memory sqlite, minimal
INSTALLED_APPS), then `django.setup()`. Ad-hoc models need `app_label` and
`schema_editor().create_model(...)`.
