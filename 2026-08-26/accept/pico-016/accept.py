#!/usr/bin/env python
"""Acceptance probe for pico-016 (world: sphinx-doc__sphinx-9229).

Verdict source (policy P1): issues/pico-016.md ONLY.

  "for 2 of them, the docstrings are ignored and the only thing shown is the
   ``alias of ...`` text"
  Expected behavior: "The docs should show the contents in the docstrings for
   all the type aliases instead of the ``alias of ...`` default text."

So the issue asks for two things at once, and this probe checks both:

  A. every documented type alias renders ITS OWN docstring, and
  B. it renders that docstring *instead of* the ``alias of ...`` default text.

Fixture: a minimal sphinx project in /tmp built with the ``text`` builder,
using the issue's own example module (ScaffoldOpts / FileContents / FileOp),
autodoc + automodule/autodata.

  probe 0 (fixture self-check) -- the build must succeed and autodoc must have
      emitted an entry for each of the three aliases; otherwise the probe is
      measuring nothing -> exit 2.
  probe 1 (acceptance) -- A and B above, over the rendered text.

Exit codes: 0 acceptance met - 1 acceptance not met - 2 probe broken.
"""

import os
import re
import subprocess
import sys
import tempfile
import traceback

MODULE_NAME = "pico016_file"

MODULE_SRC = '''\
# {module}.py -- reduced example from the issue
from pathlib import Path
from typing import Any, Callable, Dict, Union

# Signatures for the documentation purposes

ScaffoldOpts = Dict[str, Any]
"""Dictionary with PyScaffold's options, see ``pyscaffold.api.create_project``.
Should be treated as immutable (if required, copy before changing).

Please notice some behaviours given by the options **SHOULD** be observed.
"""

FileContents = Union[str, None]
"""When the file content is ``None``, the file should not be written to
disk (empty files are represented by an empty string as content).
"""

FileOp = Callable[[Path, FileContents, ScaffoldOpts], Union[Path, None]]
"""Signature of functions considered file operations::

    Callable[[Path, FileContents, ScaffoldOpts], Union[Path, None]]

- **path**: file path potentially to be written to/changed in the disk.
- **contents**: usually a string that represents a text content of the file.
- **opts**: a dict with PyScaffold's options.
"""
'''.format(module=MODULE_NAME)

CONF_SRC = '''\
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

project = "pico016"
master_doc = "index"
extensions = ["sphinx.ext.autodoc"]
exclude_patterns = ["_build"]
'''

INDEX_SRC = """\
Type alias docstrings
=====================

.. automodule:: {module}

.. autodata:: {module}.ScaffoldOpts

.. autodata:: {module}.FileContents

.. autodata:: {module}.FileOp
""".format(module=MODULE_NAME)

# (alias name, a distinctive phrase from that alias's own docstring)
ALIASES = [
    ("ScaffoldOpts", "Dictionary with PyScaffold's options"),
    ("FileContents", "the file should not be written to disk"),
    ("FileOp", "Signature of functions considered file operations"),
]

BOILERPLATE = "alias of"


def normalize(text):
    """Collapse the text builder's line wrapping so phrases match contiguously."""
    return re.sub(r"\s+", " ", text)


def build_project(root):
    srcdir = os.path.join(root, "src")
    outdir = os.path.join(root, "out")
    os.makedirs(srcdir)
    for name, body in (
        (MODULE_NAME + ".py", MODULE_SRC),
        ("conf.py", CONF_SRC),
        ("index.rst", INDEX_SRC),
    ):
        with open(os.path.join(srcdir, name), "w") as handle:
            handle.write(body)

    cmd = [sys.executable, "-m", "sphinx", "-b", "text", "-E", srcdir, outdir]
    env = dict(os.environ)
    env["HOME"] = root
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    out, err = proc.communicate(timeout=600)
    return proc.returncode, out, err, os.path.join(outdir, "index.txt")


def main():
    root = tempfile.mkdtemp(prefix="pico016_")
    rc, out, err, index_txt = build_project(root)

    # ---------------------------------------------------------------- probe 0
    if rc != 0 or not os.path.exists(index_txt):
        print(
            "probe 0 (fixture self-check): BROKEN - sphinx-build -b text failed "
            "(rc=%d, index.txt exists=%s); stdout[-400:]=%r stderr[-400:]=%r"
            % (rc, os.path.exists(index_txt), out[-400:], err[-400:])
        )
        return 2

    with open(index_txt) as handle:
        rendered = handle.read()
    flat = normalize(rendered)

    missing_entries = [
        name for name, _ in ALIASES if ("%s.%s" % (MODULE_NAME, name)) not in flat
    ]
    if missing_entries:
        print(
            "probe 0 (fixture self-check): BROKEN - autodoc emitted no entry for "
            "%s in the rendered text (%d chars); the fixture is not documenting "
            "the type aliases at all. stderr[-400:]=%r"
            % (missing_entries, len(rendered), err[-400:])
        )
        return 2
    print(
        "probe 0 (fixture self-check): OK - sphinx text build succeeded and "
        "autodoc emitted entries for %s from module %s."
        % ([name for name, _ in ALIASES], MODULE_NAME)
    )

    # ---------------------------------------------------------------- probe 1
    docstring_missing = [
        name for name, phrase in ALIASES if phrase.lower() not in flat.lower()
    ]
    boilerplate_hits = len(re.findall(re.escape(BOILERPLATE), flat, re.IGNORECASE))

    if docstring_missing or boilerplate_hits:
        problems = []
        if docstring_missing:
            problems.append(
                "docstring ignored for %s (their own docstring text is absent "
                "from the rendered output)" % docstring_missing
            )
        if boilerplate_hits:
            snippet = ""
            match = re.search(
                re.escape(BOILERPLATE) + r".{0,80}", flat, re.IGNORECASE
            )
            if match:
                snippet = match.group(0)
            problems.append(
                "the %r default text is still rendered %d time(s) for aliases "
                "that carry their own docstring (first: %r)"
                % (BOILERPLATE, boilerplate_hits, snippet)
            )
        print(
            "probe 1 (acceptance, alias docstrings win over the default text): "
            "FAIL - %s. The issue asks for the docstring contents to be shown "
            "for all type aliases instead of the 'alias of ...' default text."
            % "; and ".join(problems)
        )
        return 1

    print(
        "probe 1 (acceptance, alias docstrings win over the default text): PASS - "
        "all %d type aliases (%s) render their own docstring and the 'alias of "
        "...' default text appears 0 times in the rendered output (%d chars)."
        % (len(ALIASES), ", ".join(n for n, _ in ALIASES), len(rendered))
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
