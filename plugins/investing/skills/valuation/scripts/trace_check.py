#!/usr/bin/env python3
"""
trace_check.py — every number in a draft must trace to a script run or a dated source.

Implements
----------
  A number in the draft passes when it matches, within its printed precision:
    - any numeric output of a run in the manifest (valuation, screens, sizing), or
    - a `value` in the sources file, each entry carrying `source` and `as_of`, or
    - an allow-comment in the draft: <!-- allow: 3 reason=three scenarios -->
  Percentages are matched both as written (25%) and as fractions (0.25).
  Years (1900-2100), dates, and list ordinals are ignored.

Sources file (JSON list):
  [{"label": "share price", "value": 48.2, "source": "<exchange or filing URL>", "as_of": "2026-10-29"}]
  Entries without `source` or `as_of` fail: an undated number is not a source.

Exit 0 when every number traces, 1 otherwise. This checks attachment, not truth:
a number can trace to a wrong source. Load-bearing inputs are verified separately
(references/analyse.md, input checks).

Usage
-----
  trace_check.py --draft draft.md [--manifest manifest.json] [--sources sources.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NUM = re.compile(r"(?<![\w.])[-−]?\d[\d,]*(?:\.\d+)?%?")
ALLOW = re.compile(r"<!--\s*allow:\s*([-\d.,%]+)\s+reason=[^>]*-->")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def collect(obj, acc: list[float]) -> list[float]:
    if isinstance(obj, bool):
        return acc
    if isinstance(obj, (int, float)):
        acc.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            collect(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, acc)
    return acc


def matches(token: str, known: list[float]) -> bool:
    pct = token.endswith("%")
    s = token.rstrip("%").replace(",", "").replace("−", "-")
    val = float(s)
    decimals = len(s.split(".")[1]) if "." in s else 0
    tol = 0.5 * 10 ** -decimals + 1e-9
    targets = [val / 100, val] if pct else [val]
    for t in targets:
        t_tol = tol / 100 if (pct and t == val / 100) else tol
        if any(abs(k - t) <= t_tol for k in known):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--sources")
    args = ap.parse_args()
    text = Path(args.draft).read_text()
    known: list[float] = []
    problems: list[str] = []
    if args.manifest:
        for run in json.loads(Path(args.manifest).read_text()).get("runs", []):
            collect(run.get("outputs", {}), known)
    if args.sources:
        for i, s in enumerate(json.loads(Path(args.sources).read_text())):
            if not s.get("source") or not s.get("as_of"):
                problems.append(f"sources[{i}] ({s.get('label', '?')}) lacks source or as_of")
                continue
            collect(s.get("value"), known)
    for m in ALLOW.finditer(text):
        known.append(float(m.group(1).rstrip("%").replace(",", "")))
    body = DATE.sub(" ", ALLOW.sub(" ", text))
    body = re.sub(r"^\s*\d+\.\s", " ", body, flags=re.M)  # numbered-list markers
    unsourced = []
    audited = 0
    for m in NUM.finditer(body):
        tok = m.group(0)
        plain = tok.rstrip("%").replace(",", "")
        if re.fullmatch(r"(19|20)\d\d", plain):
            continue
        audited += 1
        if not matches(tok, known):
            unsourced.append(tok)
    report = {"numbers_audited": audited, "unsourced": sorted(set(unsourced)), "problems": problems}
    print(json.dumps(report, indent=2))
    return 1 if unsourced or problems else 0


if __name__ == "__main__":
    sys.exit(main())
