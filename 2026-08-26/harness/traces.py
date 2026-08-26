"""Trace reading helpers. The traj format is pico-1 (ch02 schema); the runner
writes it via bench/swebench_mini.make_traj and this module only reads it."""

import json
from pathlib import Path


def load_traj(path: Path) -> dict:
    return json.loads(path.read_text())


def final_text(traj: dict) -> str:
    """The agent's last assistant text — its submit report."""
    for m in reversed(traj["messages"]):
        if m["role"] != "assistant":
            continue
        text = "".join(b["text"] for b in m["content"] if b["kind"] == "text")
        if text.strip():
            return text
    return ""


def tool_events(traj: dict) -> list[dict]:
    """Flatten calls and results into [{name, args, output}] in order."""
    calls: dict[str, dict] = {}
    events = []
    for m in traj["messages"]:
        for b in m["content"]:
            if b["kind"] == "tool_call":
                ev = {"name": b["name"], "args": b["arguments"], "output": ""}
                calls[b["id"]] = ev
                events.append(ev)
            elif b["kind"] == "tool_result":
                if b["call_id"] in calls:
                    calls[b["call_id"]]["output"] = b["content"]
    return events


def searchable_text(traj: dict) -> str:
    """Everything the agent typed or saw, for surface-probe scans."""
    parts = []
    for ev in tool_events(traj):
        parts.append(json.dumps(ev["args"]))
        parts.append(ev["output"])
    return "\n".join(parts)
