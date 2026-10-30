#!/usr/bin/env python3
"""
corelib.py — shared plumbing for cycling-core compute scripts.

Every compute script emits a manifest run so that verify_output.py can trace
each number in a draft back to a deterministic execution. Nothing in this
module makes physiological decisions; it only records them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 1


# --------------------------------------------------------------------------- #
# manifest
# --------------------------------------------------------------------------- #

def _hash_inputs(inputs: dict) -> str:
    blob = json.dumps(inputs, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def emit(script: str, inputs: dict, outputs: dict, manifest_path: str | None,
         notes: list[str] | None = None, quiet: bool = False) -> dict:
    """Append a run to the manifest and return the run record."""
    run = {
        "id": None,
        "script": script,
        "inputs_hash": _hash_inputs(inputs),
        "inputs": inputs,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "outputs": outputs,
        "notes": notes or [],
    }
    if manifest_path:
        p = Path(manifest_path)
        data = {"version": MANIFEST_VERSION, "runs": []}
        if p.exists():
            try:
                data = json.loads(p.read_text())
            except json.JSONDecodeError:
                pass
        data.setdefault("runs", [])
        run["id"] = f"R-{len(data['runs']) + 1:02d}"
        data["runs"].append(run)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, default=str))
    else:
        run["id"] = "R-00"
    if not quiet:
        print(json.dumps({"run": run["id"], "script": script,
                          "outputs": outputs, "notes": run["notes"]},
                         indent=2, default=str))
    return run


def base_parser(description: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="path to manifest.json to append a run to")
    ap.add_argument("--quiet", action="store_true")
    return ap


# --------------------------------------------------------------------------- #
# numeric helpers
# --------------------------------------------------------------------------- #

def r(x: float, nd: int = 1) -> float:
    """Round for reporting. Compute keeps full precision; reports do not."""
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), nd)


def band(value: float, rel: float, nd: int = 1) -> dict:
    """Symmetric relative uncertainty band."""
    return {"value": r(value, nd), "lo": r(value * (1 - rel), nd),
            "hi": r(value * (1 + rel), nd), "rel_band": rel}


def require(cond: bool, msg: str) -> None:
    if not cond:
        print(f"INPUT ERROR: {msg}", file=sys.stderr)
        sys.exit(2)


def in_range(name: str, v: float, lo: float, hi: float, notes: list[str]) -> None:
    """Soft plausibility check — records a note rather than failing."""
    if v is not None and not (lo <= v <= hi):
        notes.append(f"IMPLAUSIBLE: {name}={v} outside [{lo}, {hi}]")
