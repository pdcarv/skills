#!/usr/bin/env python3
"""Rank functions by CRAP score: cyclomatic complexity from lizard, line coverage from a report.

CRAP(m) = comp(m)^2 * (1 - cov(m))^3 + comp(m)   (Savoia and Evans, crap4j, 2007)

Usage:
  python3 crap.py --coverage <report> [--threshold 30] [--top 25] [--json] <path> [<path> ...]

<report> is one of: lcov (lcov.info), Cobertura XML (coverage.py `coverage xml`),
JaCoCo XML (jacoco.xml) or a Go cover profile (`go test -coverprofile`). The format is
detected from the content. <path> is a source file or folder to analyse with lizard.

Coverage of a function is covered / executable lines between its first and last line,
excluding the signature line (Python marks `def` lines as run on import) and the lines of
functions nested inside it. A function whose file is missing from the report gets 0% and is
flagged, because "not measured" must not read as "fine". Files are listed with
`git ls-files` inside a repository (so ignored files are skipped), and byte-identical files
are all kept: lizard's own file walk drops duplicates, which are what a cleanup looks for.
Exits 1 when the report has no files or no functions were found, since an all-"n/a" table
would look like a result.

Needs the `lizard` package (pip). This script never installs it; it tells you how.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

LineHits = dict[int, int]  # line number -> hit count


def norm(path: str) -> str:
    path = os.path.normpath(path).replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def parse_lcov(text: str) -> dict[str, LineHits]:
    files: dict[str, LineHits] = {}
    current: LineHits | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("SF:"):
            current = files.setdefault(norm(line[3:]), {})
        elif line.startswith("DA:") and current is not None:
            num, hits = line[3:].split(",")[:2]
            current[int(num)] = max(current.get(int(num), 0), int(float(hits)))
        elif line == "end_of_record":
            current = None
    return files


def parse_cobertura(root: ET.Element) -> dict[str, LineHits]:
    sources = [s.text.strip() for s in root.iter("source") if s.text and s.text.strip()]
    files: dict[str, LineHits] = {}
    for cls in root.iter("class"):
        name = cls.get("filename", "")
        # coverage.py writes one <source> per root; with several roots a bare file name is ambiguous
        key = norm(os.path.join(sources[0], name)) if len(sources) == 1 else norm(name)
        if len(sources) > 1:
            existing = [norm(os.path.join(s, name)) for s in sources if os.path.exists(os.path.join(s, name))]
            key = existing[0] if len(existing) == 1 else key
        hits = files.setdefault(key, {})
        for ln in cls.iter("line"):
            n, h = int(ln.get("number", 0)), int(float(ln.get("hits", 0)))
            hits[n] = max(hits.get(n, 0), h)
    return files


def parse_jacoco(root: ET.Element) -> dict[str, LineHits]:
    files: dict[str, LineHits] = {}
    for pkg in root.iter("package"):
        for sf in pkg.iter("sourcefile"):
            hits = files.setdefault(norm(f"{pkg.get('name', '')}/{sf.get('name', '')}"), {})
            for ln in sf.iter("line"):
                hits[int(ln.get("nr", 0))] = 1 if int(ln.get("ci", 0)) > 0 else 0
    return files


GO_LINE = re.compile(r"^(.+):(\d+)\.\d+,(\d+)\.\d+ \d+ (\d+)$")


def go_module(start: str) -> str | None:
    """The module path from the nearest go.mod at or above `start`, used to strip report prefixes."""
    d = os.path.abspath(start)
    while True:
        gomod = os.path.join(d, "go.mod")
        if os.path.isfile(gomod):
            with open(gomod, encoding="utf-8") as fh:
                m = re.search(r"^module\s+(\S+)", fh.read(), re.M)
            return m.group(1) if m else None
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def parse_go(text: str, module: str | None = None) -> dict[str, LineHits]:
    files: dict[str, LineHits] = {}
    for line in text.splitlines()[1:]:
        m = GO_LINE.match(line.strip())
        if not m:
            continue
        name = m.group(1)
        if module and name.startswith(module + "/"):
            name = name[len(module) + 1:]
        hits = files.setdefault(norm(name), {})
        for n in range(int(m.group(2)), int(m.group(3)) + 1):
            hits[n] = max(hits.get(n, 0), int(m.group(4)))
    return files


def load_coverage(path: str, source_hint: str = ".") -> dict[str, LineHits]:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    head = text.lstrip()[:200]
    if head.startswith("mode:"):
        return parse_go(text, go_module(source_hint))
    if head.startswith("<"):
        root = ET.fromstring(text)
        return parse_jacoco(root) if root.tag == "report" else parse_cobertura(root)
    return parse_lcov(text)


def find_hits(coverage: dict[str, LineHits], source: str) -> LineHits | None:
    """Match a source path to a report path by the longest shared path suffix.

    A report path that is a bare file name only matches a file at the current directory's top
    level, so `util.py` in the report never claims `pkg/util.py`."""
    src = norm(os.path.abspath(source)).split("/")
    rel = norm(os.path.relpath(source))
    best, best_len = None, 0
    for cov_path, hits in coverage.items():
        parts = cov_path.split("/")
        if len(parts) == 1 and rel != cov_path:
            continue
        n = 0
        while n < min(len(parts), len(src)) and parts[-1 - n] == src[-1 - n]:
            n += 1
        full = n == len(parts) or n == len(src)
        if (full or n >= 2) and n > best_len:  # a bare file name alone is too weak a match
            best, best_len = hits, n
    return best


def function_coverage(hits: LineHits | None, start: int, end: int, skip: set[int] = frozenset()) -> float | None:
    if hits is None:
        return None
    first = start + 1 if end > start else start
    lines = [n for n in range(first, end + 1) if n in hits and n not in skip]
    if not lines:
        return None
    return sum(1 for n in lines if hits[n] > 0) / len(lines)


def crap(complexity: int, coverage: float) -> float:
    return complexity ** 2 * (1 - coverage) ** 3 + complexity


SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "target", "vendor"}


def source_files(paths: list[str], lizard) -> list[str]:
    """Every file lizard can read under `paths`, honouring .gitignore inside a git repository."""
    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
            continue
        listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", path],
                                capture_output=True, text=True)
        if listed.returncode == 0 and listed.stdout.strip():
            files += [f for f in listed.stdout.splitlines() if os.path.isfile(f)]
            continue
        for root, dirs, names in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            files += [os.path.join(root, n) for n in names]
    return sorted({f for f in files if lizard.get_reader_for(f)})


def analyse(paths: list[str], coverage: dict[str, LineHits]) -> list[dict]:
    try:
        import lizard
    except ImportError:
        sys.exit("lizard is not installed. Ask the user before installing it: "
                 "python3 -m pip install lizard (https://github.com/terryyin/lizard)")
    rows = []
    for info in lizard.analyze_files(source_files(paths, lizard)):
        hits = find_hits(coverage, info.filename)
        for fn in info.function_list:
            nested = {n for other in info.function_list if other is not fn
                      and fn.start_line < other.start_line and other.end_line <= fn.end_line
                      for n in range(other.start_line, other.end_line + 1)}
            cov = function_coverage(hits, fn.start_line, fn.end_line, nested)
            rows.append({
                "file": info.filename, "line": fn.start_line, "function": fn.name,
                "complexity": fn.cyclomatic_complexity, "nloc": fn.nloc,
                "coverage": None if cov is None else round(cov, 3),
                "measured": cov is not None,
                "crap": round(crap(fn.cyclomatic_complexity, cov or 0.0), 1),
            })
    return sorted(rows, key=lambda r: (-r["crap"], -r["complexity"], r["file"], r["line"]))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--coverage", required=True, help="lcov, Cobertura XML, JaCoCo XML or Go cover profile")
    ap.add_argument("--threshold", type=float, default=30.0, help="CRAP score that counts as crappy (crap4j default 30)")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--json", action="store_true", help="print all rows as JSON")
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args(argv)
    coverage = load_coverage(a.coverage, a.paths[0])
    if not coverage:
        print(f"no files found in coverage report {a.coverage}: is it lcov, Cobertura, JaCoCo or a Go profile?",
              file=sys.stderr)
        return 1
    rows = analyse(a.paths, coverage)
    if not rows:
        print(f"no functions found under {' '.join(a.paths)}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps({"threshold": a.threshold, "functions": rows}, indent=2))
        return 0
    over = [r for r in rows if r["crap"] > a.threshold]
    unmeasured = sum(1 for r in rows if not r["measured"])
    print(f"{len(rows)} functions, {len(over)} above CRAP {a.threshold:g}, {unmeasured} without coverage data\n")
    print(f"{'CRAP':>7} {'CCN':>4} {'cov':>5}  location  function")
    for r in rows[: a.top]:
        cov = "  n/a" if not r["measured"] else f"{r['coverage']:>5.0%}"
        print(f"{r['crap']:>7.1f} {r['complexity']:>4} {cov}  {r['file']}:{r['line']}  {r['function']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
