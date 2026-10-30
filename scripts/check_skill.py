#!/usr/bin/env python3
"""Lint one or more skill folders against this library's CONTRIBUTING.md rules.

Usage: python3 check_skill.py <skill-dir> [<skill-dir> ...]
Exit code 0 when no errors (warnings allowed), 1 when any error, 2 on bad usage.
Standard library only; no packages to install.
"""
import os
import re
import sys

ALLOWED_FIELDS = {"name", "description", "license", "metadata"}
TOOL_SPECIFIC = {
    "context", "paths", "globs", "disable-model-invocation", "allowed-tools",
    "disallowed-tools", "agent", "hooks", "model", "effort", "when_to_use",
    "argument-hint", "arguments", "user-invocable", "shell", "background",
    "icon", "color",
}
SECTIONS = [
    "When to use", "When not to use", "Inputs to gather", "Procedure",
    "Verification", "Gotchas", "Output", "Sources",
]
# Domain plugins hold stateful, self-contained skills (roles/, state/, compute
# scripts) whose structure does not fit the procedure template; they skip the
# section check but keep every frontmatter and portability rule.
DOMAIN_PLUGINS = {"training", "investing"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):(.*)$")
CHILD_RE = re.compile(r"^\s+([A-Za-z0-9_-]+):(.*)$")


def parse_frontmatter(lines):
    """Return (fields, metadata, body_start, errors) for simple YAML frontmatter."""
    errors = []
    if not lines or lines[0].strip() != "---":
        return {}, {}, 0, ["SKILL.md must start with '---' frontmatter"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, {}, 0, ["frontmatter has no closing '---'"]
    fields, metadata = {}, {}
    i = 1
    while i < end:
        line = lines[i]
        m = KEY_RE.match(line)
        if not m:
            if line.strip():
                errors.append(f"frontmatter line {i + 1} not understood: {line.strip()[:60]}")
            i += 1
            continue
        key, raw = m.group(1), m.group(2).strip()
        i += 1
        block = []
        while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            block.append(lines[i])
            i += 1
        if key == "metadata":
            for b in block:
                if not b.strip():
                    continue
                cm = CHILD_RE.match(b)
                if not cm:
                    errors.append(f"metadata entry not a 'key: value' string: {b.strip()[:60]}")
                    continue
                val = cm.group(2).strip()
                if val == "" or val.startswith(("[", "{", "-")):
                    errors.append(f"metadata.{cm.group(1)} must be a plain string (no lists or nesting)")
                metadata[cm.group(1)] = val.strip("\"'")
            fields[key] = metadata
        elif raw in (">", ">-", "|", "|-"):
            parts = [b.strip() for b in block]
            joiner = " " if raw.startswith(">") else "\n"
            fields[key] = joiner.join(p for p in parts if p).strip()
        else:
            fields[key] = raw.strip("\"'")
    return fields, metadata, end + 1, errors


def check(skill_dir):
    errors, warnings = [], []
    skill_dir = os.path.normpath(skill_dir)
    folder = os.path.basename(skill_dir)
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [f"{path} not found"], []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    fields, metadata, body_start, fm_errors = parse_frontmatter(lines)
    errors += fm_errors

    for key in fields:
        if key in TOOL_SPECIFIC:
            errors.append(f"tool-specific field '{key}' is not allowed in this library")
        elif key not in ALLOWED_FIELDS:
            errors.append(f"field '{key}' is outside this library's portable subset (name, description, license, metadata)")

    name = fields.get("name", "")
    if not name:
        errors.append("missing 'name'")
    else:
        if len(name) > 64:
            errors.append(f"name is {len(name)} chars; max 64")
        if not NAME_RE.match(name):
            errors.append("name must be lowercase letters, digits and single hyphens, no leading/trailing hyphen")
        if name != folder:
            errors.append(f"name '{name}' does not equal folder '{folder}'")
        if "claude" in name.lower() or "anthropic" in name.lower():
            errors.append("name must not contain 'claude' or 'anthropic'")

    desc = fields.get("description", "")
    if not desc:
        errors.append("missing 'description'")
    else:
        if len(desc) > 1024:
            errors.append(f"description is {len(desc)} chars; max 1024")
        if not re.search(r"\buse (when|for|it|this)\b", desc, re.I):
            warnings.append("description has no 'Use when/for' trigger clause")
        if re.search(r"\b(I|you|we)\b", desc):
            warnings.append("description may not be third person (found I/you/we)")
        if re.search(r"<[A-Za-z/][^>]*>", desc):
            warnings.append("description contains '<...>'; Anthropic disallows XML tags in descriptions")

    if "license" not in fields:
        warnings.append("missing 'license'")
    if "category" not in metadata:
        warnings.append("metadata.category missing")

    if len(lines) >= 500:
        errors.append(f"SKILL.md has {len(lines)} lines; must be under 500")
    elif len(lines) > 200:
        warnings.append(f"SKILL.md has {len(lines)} lines; library aims for 60-200")

    body = lines[body_start:]
    if not any(l.startswith("# ") for l in body):
        errors.append("no '# Title' heading")
    headings = [l[3:].strip() for l in body if l.startswith("## ")]
    positions = []
    plugin = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(skill_dir))))
    for sec in ([] if plugin in DOMAIN_PLUGINS else SECTIONS):
        if sec not in headings:
            errors.append(f"missing section '## {sec}'")
        else:
            positions.append(headings.index(sec))
    if positions != sorted(positions):
        errors.append("sections out of order; expected: " + ", ".join(SECTIONS))

    ref_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(ref_dir):
        for fn in sorted(os.listdir(ref_dir)):
            rp = os.path.join(ref_dir, fn)
            if os.path.isdir(rp):
                errors.append(f"references/{fn} is a folder; keep references one level deep")
                continue
            with open(rp, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            if re.search(r"\]\((\./)?(references/)?[^)\s]+\.md\)", text):
                warnings.append(f"references/{fn} links to another .md file; keep references one level deep")
            if text.count("\n") > 100 and not re.search(r"(?im)^#+\s*(contents|table of contents)", text):
                warnings.append(f"references/{fn} is over 100 lines without a table of contents")
            if fn not in "\n".join(lines):
                warnings.append(f"references/{fn} is not mentioned in SKILL.md")
    if "\\" in "\n".join(l for l in lines if "](" in l):
        warnings.append("backslash in a link; use forward-slash paths")
    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    failed = False
    for d in argv[1:]:
        errors, warnings = check(d)
        status = "FAIL" if errors else "ok"
        print(f"{status}: {d}")
        for e in errors:
            print(f"  error: {e}")
        for w in warnings:
            print(f"  warning: {w}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
