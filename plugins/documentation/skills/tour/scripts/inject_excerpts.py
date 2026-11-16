#!/usr/bin/env python3
"""Fill code excerpts into a tour page from the current source files.

Usage:
  python3 inject_excerpts.py --repo <root> [--max-lines 15] <template.html> <out.html>

In the template, each excerpt is a marker on its own line:

  <!-- excerpt path/relative/to/repo.go:12-24 -->

It is replaced by a <figure class="excerpt"> holding a caption with `path:12` and the
HTML-escaped lines 12-24. Copying from the files at build time means excerpts and line
numbers cannot drift from the code. Exits 1, naming every bad marker, when a file is
missing, a range is outside the file or longer than --max-lines; the output is not written.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys

MARKER = re.compile(r"^([ \t]*)<!--\s*excerpt\s+(\S+?):(\d+)-(\d+)\s*-->[ \t]*$", re.M)


def render(repo: str, path: str, start: int, end: int, max_lines: int) -> str:
    full = os.path.join(repo, path)
    if not os.path.isfile(full):
        raise ValueError(f"{path}: file not found under {repo}")
    with open(full, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    if not 1 <= start <= end <= len(lines):
        raise ValueError(f"{path}:{start}-{end}: outside the file (1-{len(lines)})")
    if end - start + 1 > max_lines:
        raise ValueError(f"{path}:{start}-{end}: {end - start + 1} lines, max {max_lines}")
    body = html.escape("\n".join(lines[start - 1:end]))
    return (f'<figure class="excerpt"><figcaption><code>{html.escape(path)}:{start}</code>'
            f"</figcaption><pre><code>{body}</code></pre></figure>")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fill code excerpts into a tour page.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--max-lines", type=int, default=15)
    ap.add_argument("template")
    ap.add_argument("out")
    args = ap.parse_args()

    with open(args.template, encoding="utf-8") as f:
        text = f.read()
    errors: list[str] = []

    def sub(m: re.Match[str]) -> str:
        try:
            return m.group(1) + render(args.repo, m.group(2), int(m.group(3)), int(m.group(4)), args.max_lines)
        except ValueError as e:
            errors.append(str(e))
            return m.group(0)

    out, count = MARKER.subn(sub, text)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if count == 0:
        print("no excerpt markers found", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"{count} excerpts written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
