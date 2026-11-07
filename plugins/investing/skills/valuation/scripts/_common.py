"""Shared plumbing for the valuation scripts: JSON input, manifest runs, errors.

Every script prints one JSON object with `outputs` and `notes`, and can append the
run to a manifest so `trace_check.py` can trace each number in a draft back to it.
Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn


def fail(msg: str) -> NoReturn:
    print(f"INPUT ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def load_input(path: str | None) -> dict:
    """Read a JSON object from a file, or from stdin when path is '-' or None."""
    try:
        text = sys.stdin.read() if path in (None, "-") else Path(path).read_text()
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as e:
        fail(f"could not read JSON input: {e}")
    if not isinstance(data, dict):
        fail("input must be a JSON object")
    return data


def r(x, nd=2):
    return None if x is None else round(float(x), nd)


def emit(script: str, inputs: dict, outputs: dict, notes: list[str], manifest: str | None) -> None:
    run = {"script": script,
           "inputs_hash": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12],
           "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "outputs": outputs, "notes": notes}
    if manifest:
        p = Path(manifest)
        data = {"runs": []}
        if p.exists():
            try:
                data = json.loads(p.read_text())
            except json.JSONDecodeError:
                pass
        data.setdefault("runs", [])
        run["id"] = f"R-{len(data['runs']) + 1:02d}"
        data["runs"].append(run)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))
    else:
        run["id"] = "R-00"
    print(json.dumps({"run": run["id"], "script": script, "outputs": outputs, "notes": notes}, indent=2))
