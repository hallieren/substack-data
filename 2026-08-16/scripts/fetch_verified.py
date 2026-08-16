"""One-shot: fetch SWE-bench Verified (500 instances) via the HF datasets-server API.

Writes bench/instances_verified.json with just what the runner needs.
Run: uv run python bench/fetch_verified.py
"""

import json
from pathlib import Path

import httpx

URL = "https://datasets-server.huggingface.co/rows"
DATASET = "princeton-nlp/SWE-bench_Verified"


def main() -> None:
    rows, offset = [], 0
    while True:
        r = httpx.get(
            URL,
            params={"dataset": DATASET, "config": "default", "split": "test",
                    "offset": offset, "length": 100},
            timeout=60,
        )
        r.raise_for_status()
        batch = r.json()["rows"]
        if not batch:
            break
        rows += [{"instance_id": x["row"]["instance_id"],
                  "problem_statement": x["row"]["problem_statement"],
                  "base_commit": x["row"]["base_commit"]} for x in batch]
        offset += len(batch)
    assert len(rows) == 500, f"expected 500 instances, got {len(rows)}"
    out = Path(__file__).parent / "instances_verified.json"
    out.write_text(json.dumps(rows))
    print(f"wrote {len(rows)} instances to {out}")


if __name__ == "__main__":
    main()
