"""redact_baits — replace the bait texts in attacks/*.yaml with [redacted]
before the folder is published. The full texts stay with the author
(daily/articles/2026-09-02/evidence/baits.local/). Idempotent."""

import re
from pathlib import Path

ATTACKS = Path(__file__).resolve().parent.parent / "attacks"

for p in sorted(ATTACKS.glob("atk-*.yaml")):
    t = p.read_text()
    t = re.sub(r"(  issue_append: \|\n)(?:    .*\n)+", r"\1    [redacted, see baits.redacted.md]\n", t)
    t = re.sub(r"(  comment: \|\n)(?:    .*\n)+", r"\1    # [redacted, see baits.redacted.md]\n", t)
    p.write_text(t)
    print("redacted", p.name)
