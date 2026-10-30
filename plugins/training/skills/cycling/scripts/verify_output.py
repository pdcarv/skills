#!/usr/bin/env python3
"""
verify_output.py — mechanical audit gate for cycling-core outputs.

Converts "be careful not to hallucinate" from an instruction the model follows
inconsistently into a gate that either passes or does not.

Checks (see protocols/verification.md):
  NUMERIC     every numeric token in the draft traces to a ledger row, a compute
              manifest run, the athlete profile, or an explicit allow-comment
  CITATION    every (Author, Year) pattern traces to a RETRIEVED ledger row with a URL
  CONFIDENCE  every asserted confidence level equals the P3 rubric value
  RECENCY     no high-volatility row is used past its staleness threshold unchecked
  QUOTE       no verbatim span >=15 words; at most one quoted span per source
  UNITS       quantities fall inside physiological plausibility bands
  PROFILE     no draft value contradicts a verify-keys anchor without a supersede block

Usage:
  verify_output.py --draft d.md --ledger l.yaml [--manifest m.json]
                   [--profile p.yaml] [--frameworks f.yaml]
                   [--session-date YYYY-MM-DD] [--json] [--strict]

Exit codes: 0 clean (warnings allowed) | 1 errors present | 2 bad invocation
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required", file=sys.stderr)
    sys.exit(2)

# --------------------------------------------------------------------------- #
# findings
# --------------------------------------------------------------------------- #

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    context: str = ""

    def render(self) -> str:
        ctx = f"  |  …{self.context}…" if self.context else ""
        return f"[{self.severity:5}] {self.check:10} {self.message}{ctx}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add(self, check, severity, message, context="") -> None:
        self.findings.append(Finding(check, severity, message, context))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == WARN]


# --------------------------------------------------------------------------- #
# draft preprocessing
# --------------------------------------------------------------------------- #

FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
ALLOW_RE = re.compile(r"allow:\s*([-\d.,\s]+?)\s+reason=(.+)", re.S)
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$", re.M)


def strip_noise(text: str) -> tuple[str, list[str], set[str]]:
    """Remove code, comments and table rules. Return (prose, comments, allowed_numbers)."""
    comments = COMMENT_RE.findall(text)
    allowed: set[str] = set()
    for c in comments:
        m = ALLOW_RE.search(c)
        if m:
            for tok in re.split(r"[,\s]+", m.group(1).strip()):
                if tok:
                    allowed.add(normalise_num(tok))
    prose = COMMENT_RE.sub(" ", text)
    prose = FENCE_RE.sub(" ", prose)
    prose = INLINE_CODE_RE.sub(" ", prose)
    prose = TABLE_SEP_RE.sub(" ", prose)
    return prose, comments, allowed


def normalise_num(tok: str) -> str:
    tok = tok.replace(",", "").replace("\u2212", "-").strip()
    try:
        v = float(tok)
    except ValueError:
        return tok
    return f"{v:.6g}"


# numbers to ignore entirely: ids, ISO dates, markdown/section scaffolding
IGNORE_PATTERNS = [
    re.compile(r"\bL-\d{4}\b"),
    re.compile(r"\bR-\d{2}\b"),
    re.compile(r"\bC-\d{3}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\bhttps?://\S+"),
    re.compile(r"§\s*\d+(\.\d+)*"),
    re.compile(r"^\s*#{1,6}\s*\d+(\.\d+)*", re.M),
    re.compile(r"^\s*\d+\.\s", re.M),          # ordered list markers
    re.compile(r"\bStep\s+\d+\b", re.I),
    re.compile(r"\bPhase\s+\d+\b", re.I),
    re.compile(r"\bWeek\s+\d+\b", re.I),
    re.compile(r"\bBlock\s+\d+\b", re.I),
    re.compile(r"\bv\d+(\.\d+)*\b", re.I),      # version strings
    re.compile(r"\bDOI:\s*\S+", re.I),
    re.compile(r"\b10\.\d{4,}/\S+"),            # bare DOIs
]

NUM_RE = re.compile(r"(?<![\w/.-])[-−]?\d+(?:,\d{3})*(?:\.\d+)?(?![\w.-])")


def extract_numbers(prose: str) -> list[tuple[str, str]]:
    """Return [(normalised_value, context_snippet)] for auditable numbers."""
    masked = prose
    for pat in IGNORE_PATTERNS:
        masked = pat.sub(lambda m: " " * len(m.group(0)), masked)
    out = []
    for m in NUM_RE.finditer(masked):
        raw = m.group(0)
        val = normalise_num(raw)
        try:
            f = float(val)
        except ValueError:
            continue
        # bare 4-digit years are handled by the CITATION check
        if f.is_integer() and 1900 <= f <= 2100 and "." not in raw:
            continue
        lo, hi = max(0, m.start() - 45), min(len(prose), m.end() + 45)
        ctx = re.sub(r"\s+", " ", prose[lo:hi]).strip()
        out.append((val, ctx))
    return out


# --------------------------------------------------------------------------- #
# value universe (what a number is allowed to be)
# --------------------------------------------------------------------------- #

SCALES = [1.0, 0.001, 1000.0, 0.01, 100.0, 60.0, 1 / 60.0]


def flatten(obj: Any, out: set[str] | None = None) -> set[str]:
    out = set() if out is None else out
    if isinstance(obj, dict):
        for v in obj.values():
            flatten(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            flatten(v, out)
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out.add(normalise_num(str(obj)))
    elif isinstance(obj, str):
        for m in NUM_RE.finditer(obj):
            out.add(normalise_num(m.group(0)))
    return out


def build_universe(ledger, manifest, profile) -> tuple[set[str], set[str]]:
    """Return (exact_values, derived_values) — derived includes unit rescalings."""
    exact: set[str] = set()
    for row in ledger:
        for key in ("effect", "design", "population"):
            if row.get(key):
                flatten(row[key], exact)
    for run in (manifest or {}).get("runs", []):
        flatten(run.get("outputs", {}), exact)
    flatten(profile or {}, exact)

    derived: set[str] = set()
    for v in exact:
        try:
            f = float(v)
        except ValueError:
            continue
        for s in SCALES:
            derived.add(normalise_num(str(f * s)))
    return exact, derived


def close_match(val: str, universe: set[str], rel_tol: float = 0.005) -> bool:
    if val in universe:
        return True
    try:
        f = float(val)
    except ValueError:
        return False
    if f == 0:
        return "0" in universe
    for u in universe:
        try:
            g = float(u)
        except ValueError:
            continue
        if g != 0 and abs(f - g) / abs(g) <= rel_tol:
            return True
    return False


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #

def check_numeric(prose, ledger, manifest, profile, allowed, rep: Report) -> None:
    exact, derived = build_universe(ledger, manifest, profile)
    nums = extract_numbers(prose)
    rep.stats["numbers_audited"] = len(nums)
    unmatched = 0
    seen: set[tuple[str, str]] = set()
    for val, ctx in nums:
        if val in allowed:
            continue
        if close_match(val, exact):
            continue
        if close_match(val, derived):
            rep.add("NUMERIC", INFO, f"{val} matched only after unit rescaling", ctx)
            continue
        key = (val, ctx[:30])
        if key in seen:
            continue
        seen.add(key)
        unmatched += 1
        rep.add("NUMERIC", ERROR, f"unsourced number {val}", ctx)
    rep.stats["numbers_unsourced"] = unmatched


CITE_RE = re.compile(
    r"\(([A-ZÀ-ÖØ-Þ][\w'’\-øæåüöéíñ]+(?:\s+(?:et al\.|and|&|,)\s*[\w'’\-øæåüöéíñ]+)*)"
    r"[,\s]+(?:et al\.[,\s]*)?(\d{4})[a-z]?\b[^)]*\)"
)
CITE_NARRATIVE_RE = re.compile(
    r"\b([A-ZÀ-ÖØ-Þ][\w'’\-øæåüöéíñ]+)\s+(?:et al\.|and colleagues)\s*\((\d{4})\)"
)
# bare "Surname (2013)" — the commonest way a fabricated citation enters prose
CITE_BARE_RE = re.compile(
    r"\b([A-ZÀ-ÖØ-Þ][a-zà-öø-þ'’\-øæåüöéíñ]{2,})\s*\((\d{4})[a-z]?\)"
)
CITE_STOPWORDS = {
    "figure", "table", "appendix", "section", "since", "the", "this", "in", "see",
    "note", "version", "update", "step", "phase", "block", "week", "revision",
}


def check_citation(prose, ledger, session_date, rep: Report) -> None:
    retrieved = [r for r in ledger if r.get("provenance") == "RETRIEVED"]
    index: list[tuple[str, str, dict]] = []
    for r in retrieved:
        src = r.get("source") or {}
        authors = (src.get("authors") or "").lower()
        year = str(src.get("year") or "")
        index.append((authors, year, r))

    cites = [(m.group(1), m.group(2)) for m in CITE_RE.finditer(prose)]
    cites += [(m.group(1), m.group(2)) for m in CITE_NARRATIVE_RE.finditer(prose)]
    cites += [(m.group(1), m.group(2)) for m in CITE_BARE_RE.finditer(prose)
              if m.group(1).lower() not in CITE_STOPWORDS]
    cites = list(dict.fromkeys(cites))
    rep.stats["citations_audited"] = len(cites)

    orphan = 0
    for author, year in cites:
        surname = author.split()[0].lower().strip(",")
        hit = None
        for authors, yr, row in index:
            if surname in authors and (not yr or yr == year):
                hit = row
                break
        if hit is None:
            orphan += 1
            rep.add("CITATION", ERROR,
                    f"orphan citation ({author}, {year}) — no RETRIEVED ledger row",
                    "")
            continue
        src = hit.get("source") or {}
        if not src.get("url"):
            rep.add("CITATION", ERROR,
                    f"({author}, {year}) maps to {hit['id']} which has no URL", "")
        elif src.get("retrieved") and session_date:
            got = _as_date(src["retrieved"])
            if got and (session_date - got).days > 0:
                rep.add("CITATION", WARN,
                        f"({author}, {year}) retrieved {got}, not this session", "")
    rep.stats["citations_orphan"] = orphan

    for r in ledger:
        if r.get("provenance") == "RECALLED":
            for k in ("source", "effect"):
                if r.get(k):
                    rep.add("CITATION", ERROR,
                            f"{r['id']} is RECALLED but carries a '{k}' block — "
                            "RECALLED may never carry citation or effect data", "")


def _as_date(v) -> date | None:
    if isinstance(v, date):
        return v
    if isinstance(v, datetime):
        return v.date()
    try:
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


# ---- P3 rubric ------------------------------------------------------------ #

DESIGN_WEIGHT = {
    "meta-analysis": 1.0, "systematic-review": 1.0, "rct": 0.85, "crossover": 0.8,
    "cohort": 0.6, "consensus": 0.5, "practitioner": 0.3, "n-of-1": 0.15,
    "unknown": 0.2,
}
POP_MATCH = {"yes": 1.0, "partial": 0.7, "no": 0.4}
REPLICATION = {"replicated": 1.0, "single": 0.6, "contested": 0.35}
PROV_CAP = {"RECALLED": 2, "STATED": 3, "STORED": 5, "RETRIEVED": 5, "COMPUTED": 5}


def _norm_bool_word(v) -> str:
    """YAML 1.1 turns bare yes/no into booleans. Recover the intended token."""
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v).lower()


def rubric_level(row: dict, stale: bool) -> int:
    d = DESIGN_WEIGHT.get(str((row.get("design") or {}).get("type", "unknown")).lower(), 0.2)
    p = POP_MATCH.get(_norm_bool_word((row.get("transfer") or {}).get("verdict", "partial")), 0.7)
    r = REPLICATION.get(str(row.get("replication", "single")).lower(), 0.6)
    rec = 0.5 if stale else 1.0
    score = d * p * r * rec
    level = (5 if score >= 0.80 else 4 if score >= 0.60 else
             3 if score >= 0.40 else 2 if score >= 0.20 else 1)
    return min(level, PROV_CAP.get(row.get("provenance", "RECALLED"), 2))


LEVEL_TAG_RE = re.compile(r"\[\[\s*(L-\d{4})\s+L([1-5])\s*\]\]")
BARE_LEVEL_RE = re.compile(r"\bConfidence\s+Level\s+([1-5])\b", re.I)


def check_confidence(prose, ledger, stale_ids, rep: Report) -> None:
    by_id = {r["id"]: r for r in ledger if "id" in r}
    tagged = LEVEL_TAG_RE.findall(prose)
    rep.stats["confidence_tags"] = len(tagged)
    for lid, asserted in tagged:
        row = by_id.get(lid)
        if row is None:
            rep.add("CONFIDENCE", ERROR, f"tag references unknown ledger id {lid}")
            continue
        expected = rubric_level(row, lid in stale_ids)
        if int(asserted) != expected:
            rep.add("CONFIDENCE", ERROR,
                    f"{lid} asserted Level {asserted}, rubric computes Level {expected}")
    bare = BARE_LEVEL_RE.findall(prose)
    if bare and not tagged:
        rep.add("CONFIDENCE", ERROR,
                f"{len(bare)} bare 'Confidence Level N' assertion(s) with no [[L-id Ln]] anchor")


def check_recency(ledger, frameworks, session_date, rep: Report) -> set[str]:
    domains = (frameworks or {}).get("domains", {})
    stale: set[str] = set()
    for row in ledger:
        dom = row.get("domain")
        meta = domains.get(dom)
        if meta is None:
            rep.add("RECENCY", WARN, f"{row.get('id')} has domain '{dom}' not in frameworks.md")
            continue
        pub = _as_date(row.get("published"))
        if pub is None or session_date is None:
            continue
        months = (session_date - pub).days / 30.44
        limit = meta.get("stale_after_months", 60)
        if months > limit:
            if _as_date(row.get("recency_checked")) == session_date:
                rep.add("RECENCY", INFO,
                        f"{row['id']} is {months:.0f}mo old (limit {limit}) but re-checked today")
            else:
                stale.add(row["id"])
                rep.add("RECENCY", ERROR,
                        f"{row['id']} domain '{dom}' is {months:.0f}mo old "
                        f"(limit {limit}) and not re-checked this session")
    rep.stats["stale_rows"] = len(stale)
    return stale


QUOTE_RE = re.compile(r"[“\"]([^”\"]{12,}?)[”\"]", re.S)
BLOCKQUOTE_RE = re.compile(r"^>\s?(.+)$", re.M)


def check_quotes(prose, ledger, rep: Report) -> None:
    flat = re.sub(r"\s+", " ", prose)          # so line-wrapped quotes are still measured
    spans = [m.group(1) for m in QUOTE_RE.finditer(flat)]
    spans += [m.group(1) for m in BLOCKQUOTE_RE.finditer(prose)]
    rep.stats["quoted_spans"] = len(spans)
    for s in spans:
        n = len(s.split())
        if n >= 15:
            rep.add("QUOTE", ERROR, f"quoted span is {n} words (limit 14)", s[:60])
    anchors: dict[str, list[str]] = {}
    for r in ledger:
        a = r.get("anchor")
        if not a:
            continue
        if len(a.split()) >= 15:
            rep.add("QUOTE", ERROR, f"{r['id']} anchor is {len(a.split())} words (limit 14)")
        url = ((r.get("source") or {}).get("url") or r["id"])
        anchors.setdefault(url, []).append(r["id"])
    for url, ids in anchors.items():
        if len(ids) > 1:
            rep.add("QUOTE", ERROR,
                    f"{len(ids)} anchors from one source ({', '.join(ids)}) — limit is one")


BANDS = {
    "W":      (0, 2500,  r"\bW\b"),
    "kg":     (25, 200,  r"\bkg\b"),
    "bpm":    (25, 230,  r"\bbpm\b"),
    "mmol/L": (0, 30,    r"\bmmol/?L?\b"),
    "W/kg":   (0, 30,    r"\bW/kg\b"),
    "kJ":     (0, 15000, r"\bkJ\b"),
    "g/h":    (0, 300,   r"\bg/h\b"),
    "mm":     (0, 1500,  r"\bmm\b"),
    "°C":     (-30, 60,  r"°C"),
    "rpm":    (0, 250,   r"\brpm\b"),
}
QTY_RE = re.compile(
    r"([-−]?\d+(?:,\d{3})*(?:\.\d+)?)\s*"
    r"(W/kg|mmol/?L|kJ|g/h|bpm|rpm|kg|mm|°C|W)\b"
)


def check_units(prose, rep: Report) -> None:
    n = 0
    for m in QTY_RE.finditer(prose):
        raw, unit = m.group(1), m.group(2)
        key = {"mmolL": "mmol/L", "mmol/L": "mmol/L"}.get(unit, unit)
        band = BANDS.get(key)
        if not band:
            continue
        n += 1
        try:
            v = float(normalise_num(raw))
        except ValueError:
            continue
        lo, hi = band[0], band[1]
        if not (lo <= v <= hi):
            lo2, hi2 = max(0, m.start() - 40), min(len(prose), m.end() + 40)
            rep.add("UNITS", ERROR, f"{v} {key} outside plausibility band [{lo}, {hi}]",
                    re.sub(r"\s+", " ", prose[lo2:hi2]).strip())
    rep.stats["quantities_checked"] = n


SUPERSEDE_RE = re.compile(r"<!--\s*supersede:\s*([\w.]+)\s+reason=(.+?)-->", re.S)


def check_profile(text, prose, profile, rep: Report) -> None:
    if not profile:
        return
    superseded = {m.group(1) for m in SUPERSEDE_RE.finditer(text)}
    checked = 0
    for key, spec in (profile.get("verify_keys") or {}).items():
        if key in superseded:
            rep.add("PROFILE", INFO, f"{key} explicitly superseded in draft")
            continue
        aliases = spec.get("aliases", [key])
        expect = spec.get("value")
        unit = spec.get("unit", "")
        if expect is None:
            continue
        for alias in aliases:
            for m in re.finditer(re.escape(alias), prose, re.I):
                window = prose[m.end(): m.end() + 60]
                nm = NUM_RE.search(window)
                if not nm:
                    continue
                checked += 1
                try:
                    got = float(normalise_num(nm.group(0)))
                except ValueError:
                    continue
                if abs(got - float(expect)) / max(abs(float(expect)), 1e-9) > 0.01:
                    rep.add("PROFILE", ERROR,
                            f"draft states {alias} = {got}{unit}, profile holds "
                            f"{expect}{unit}; no supersede block for '{key}'",
                            re.sub(r"\s+", " ", prose[m.start(): m.end() + 60]).strip())
    rep.stats["profile_keys_checked"] = checked


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #

def load_yaml(p: Path | None):
    if not p:
        return None
    return yaml.safe_load(p.read_text()) or None


def run(args) -> Report:
    text = Path(args.draft).read_text()
    ledger = load_yaml(Path(args.ledger)) if args.ledger else []
    ledger = ledger or []
    manifest = json.loads(Path(args.manifest).read_text()) if args.manifest else None
    profile = load_yaml(Path(args.profile)) if args.profile else None
    frameworks = load_yaml(Path(args.frameworks)) if args.frameworks else None
    session_date = (_as_date(args.session_date) if args.session_date else date.today())

    prose, _comments, allowed = strip_noise(text)
    rep = Report()
    rep.stats["ledger_rows"] = len(ledger)
    rep.stats["session_date"] = str(session_date)

    stale = check_recency(ledger, frameworks, session_date, rep)
    check_numeric(prose, ledger, manifest, profile, allowed, rep)
    check_citation(prose, ledger, session_date, rep)
    check_confidence(prose, ledger, stale, rep)
    check_quotes(prose, ledger, rep)
    check_units(prose, rep)
    check_profile(text, prose, profile, rep)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--ledger")
    ap.add_argument("--manifest")
    ap.add_argument("--profile")
    ap.add_argument("--frameworks")
    ap.add_argument("--session-date")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    rep = run(args)

    if args.json:
        print(json.dumps({
            "stats": rep.stats,
            "findings": [f.__dict__ for f in rep.findings],
            "errors": len(rep.errors), "warnings": len(rep.warnings),
        }, indent=2, default=str))
    else:
        order = {ERROR: 0, WARN: 1, INFO: 2}
        for f in sorted(rep.findings, key=lambda x: (order[x.severity], x.check)):
            print(f.render())
        print("\n--- stats ---")
        for k, v in rep.stats.items():
            print(f"  {k}: {v}")
        verdict = "FAIL" if rep.errors else ("FAIL (strict)" if args.strict and rep.warnings else "PASS")
        print(f"\n{verdict}  errors={len(rep.errors)} warnings={len(rep.warnings)}")

    if rep.errors or (args.strict and rep.warnings):
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # tolerate `| head`
        sys.exit(0)
