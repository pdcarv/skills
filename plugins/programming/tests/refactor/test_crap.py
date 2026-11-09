#!/usr/bin/env python3
"""Tests for refactor/scripts/crap.py. Run: python3 plugins/programming/tests/refactor/test_crap.py

Needs `lizard`; the end-to-end test also needs `coverage` and is skipped without it.
Every expected score is worked out by hand in the test's docstring.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "refactor" / "scripts" / "crap.py"
sys.path.insert(0, str(SCRIPT.parent))
import crap  # noqa: E402

SOURCE = textwrap.dedent("""\
    def simple(x):
        return x + 1


    def branchy(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        return 0
""")
# Line map: simple = 1-2 (CCN 1); branchy = 5-10 (CCN 3), body lines 6-10.


def lcov_for(path: str, hits: dict[int, int]) -> str:
    lines = "".join(f"DA:{n},{h}\n" for n, h in sorted(hits.items()))
    return f"TN:\nSF:{path}\n{lines}end_of_record\n"


class CrapScores(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.src = self.dir / "app" / "logic.py"
        self.src.parent.mkdir()
        self.src.write_text(SOURCE)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_crap(self, report_text: str, name: str = "lcov.info") -> dict[str, dict]:
        report = self.dir / name
        report.write_text(report_text)
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), "--json", str(self.src)],
                             capture_output=True, text=True, check=True)
        return {row["function"]: row for row in json.loads(out.stdout)["functions"]}

    def test_a_fully_covered_function_scores_its_complexity(self):
        """CCN 3, coverage 100%: 3^2 * 0^3 + 3 = 3."""
        rows = self.run_crap(lcov_for(str(self.src), {n: 1 for n in range(5, 11)}))
        self.assertEqual(rows["branchy"]["crap"], 3.0)

    def test_a_partly_covered_function_matches_the_formula(self):
        """Body lines 6-7 hit, 8-10 missed: cov 2/5. 9 * 0.6^3 + 3 = 4.944 -> 4.9."""
        rows = self.run_crap(lcov_for(str(self.src), {5: 1, 6: 1, 7: 1, 8: 0, 9: 0, 10: 0}))
        self.assertEqual(rows["branchy"]["coverage"], 0.4)
        self.assertEqual(rows["branchy"]["crap"], 4.9)

    def test_the_def_line_alone_does_not_count_as_covered(self):
        """Import runs the def line; the body never ran, so coverage is 0: 9 + 3 = 12."""
        rows = self.run_crap(lcov_for(str(self.src), {5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}))
        self.assertEqual(rows["branchy"]["crap"], 12.0)

    def test_a_file_missing_from_the_report_counts_as_uncovered_and_is_flagged(self):
        rows = self.run_crap(lcov_for("/elsewhere/other.py", {1: 1}))
        self.assertEqual(rows["branchy"]["crap"], 12.0)
        self.assertFalse(rows["branchy"]["measured"])

    def test_a_same_named_file_in_another_folder_is_not_matched(self):
        rows = self.run_crap(lcov_for("/elsewhere/logic.py", {n: 1 for n in range(1, 11)}))
        self.assertFalse(rows["branchy"]["measured"])

    def test_the_worst_function_is_listed_first(self):
        report = self.dir / "lcov.info"
        report.write_text(lcov_for(str(self.src), {2: 1}))
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), "--json", str(self.src)],
                             capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(out.stdout)["functions"][0]["function"], "branchy")

    def test_cobertura_report_paths_relative_to_the_source_root_are_matched(self):
        xml = (f'<coverage><sources><source>{self.dir}</source></sources><packages><package><classes>'
               '<class filename="app/logic.py"><lines>'
               + "".join(f'<line number="{n}" hits="1"/>' for n in range(5, 11))
               + "</lines></class></classes></package></packages></coverage>")
        rows = self.run_crap(xml, "coverage.xml")
        self.assertEqual(rows["branchy"]["crap"], 3.0)

    def test_jacoco_lines_with_covered_instructions_count_as_hit(self):
        xml = ('<report name="r"><package name="app"><sourcefile name="logic.py">'
               + "".join(f'<line nr="{n}" mi="0" ci="2"/>' for n in range(5, 11))
               + "</sourcefile></package></report>")
        rows = self.run_crap(xml, "jacoco.xml")
        self.assertEqual(rows["branchy"]["crap"], 3.0)

    def test_go_cover_profile_with_a_module_prefix_is_matched(self):
        profile = "mode: set\nexample.com/mod/app/logic.py:6.1,10.10 3 1\n"
        rows = self.run_crap(profile, "cover.out")
        self.assertEqual(rows["branchy"]["crap"], 3.0)

    def test_a_report_with_no_files_exits_with_an_error(self):
        report = self.dir / "lcov.info"
        report.write_text("")
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), str(self.src)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)

    def test_a_nested_function_does_not_count_toward_its_parent(self):
        """outer: own body lines 2 and 5 (one hit) -> 50%; inner's lines 3-4 are excluded."""
        nested = self.dir / "app" / "nested.py"
        nested.write_text("def outer(x):\n    y = 1\n    def inner():\n        return 2\n    return y\n")
        hits = {1: 1, 2: 1, 3: 1, 4: 1, 5: 0}
        report = self.dir / "lcov.info"
        report.write_text(lcov_for(str(nested), hits))
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), "--json", str(nested)],
                             capture_output=True, text=True, check=True)
        rows = {r["function"]: r for r in json.loads(out.stdout)["functions"]}
        self.assertEqual(rows["outer"]["coverage"], 0.5)

    def test_byte_identical_files_are_both_scored(self):
        copy = self.dir / "app" / "copy_of_logic.py"
        copy.write_text(SOURCE)
        report = self.dir / "lcov.info"
        report.write_text(lcov_for(str(self.src), {2: 1}))
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), "--json",
                              str(self.src.parent)], capture_output=True, text=True, check=True)
        files = {Path(r["file"]).name for r in json.loads(out.stdout)["functions"]}
        self.assertEqual(files, {"logic.py", "copy_of_logic.py"})

    def test_a_file_in_a_dot_folder_is_matched(self):
        hidden = self.dir / ".tools" / "gen.py"
        hidden.parent.mkdir()
        hidden.write_text(SOURCE)
        report = self.dir / "lcov.info"
        report.write_text(lcov_for("./.tools/gen.py", {n: 1 for n in range(5, 11)}))
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(report), "--json", ".tools/gen.py"],
                             capture_output=True, text=True, check=True, cwd=self.dir)
        rows = {r["function"]: r for r in json.loads(out.stdout)["functions"]}
        self.assertEqual(rows["branchy"]["crap"], 3.0)

    def test_a_bare_file_name_in_the_report_does_not_claim_a_nested_file(self):
        rows = self.run_crap(lcov_for("logic.py", {n: 1 for n in range(1, 11)}))
        self.assertFalse(rows["branchy"]["measured"])

    def test_cobertura_with_two_roots_keeps_same_named_files_apart(self):
        other = self.dir / "lib"
        other.mkdir()
        (other / "logic.py").write_text(SOURCE)
        full = "".join(f'<line number="{n}" hits="1"/>' for n in range(5, 11))
        none = "".join(f'<line number="{n}" hits="0"/>' for n in range(5, 11))
        xml = (f"<coverage><sources><source>{self.dir / 'app'}</source><source>{other}</source></sources>"
               f'<packages><package><classes><class filename="logic.py"><lines>{full}</lines></class>'
               "</classes></package></packages></coverage>")
        (self.dir / "coverage.xml").write_text(xml)
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(self.dir / "coverage.xml"), "--json",
                              str(other / "logic.py")], capture_output=True, text=True)
        self.assertNotIn('"crap": 3.0', out.stdout)

    def test_go_file_at_the_module_root_is_matched_through_go_mod(self):
        (self.dir / "go.mod").write_text("module example.com/mymod\n\ngo 1.22\n")
        main = self.dir / "main.py"
        main.write_text(SOURCE)
        (self.dir / "cover.out").write_text("mode: set\nexample.com/mymod/main.py:6.1,10.10 3 1\n")
        out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", str(self.dir / "cover.out"), "--json",
                              "main.py"], capture_output=True, text=True, check=True, cwd=self.dir)
        rows = {r["function"]: r for r in json.loads(out.stdout)["functions"]}
        self.assertEqual(rows["branchy"]["crap"], 3.0)


@unittest.skipUnless(shutil.which("coverage") or __import__("importlib").util.find_spec("coverage"),
                     "coverage.py not installed")
class RealCoveragePyReports(unittest.TestCase):
    def test_lcov_and_cobertura_from_coverage_py_give_the_same_scores(self):
        """branchy(1) runs lines 6-7 of 6-10: cov 0.4, CRAP 4.9; simple() never runs: 1 + 1 = 2."""
        work = Path(tempfile.mkdtemp())
        try:
            (work / "logic.py").write_text(SOURCE)
            (work / "main.py").write_text("from logic import branchy\nbranchy(1)\n")
            run = lambda *a: subprocess.run([sys.executable, "-m", "coverage", *a], cwd=work, check=True,
                                            capture_output=True)
            run("run", "main.py")
            run("lcov", "-o", "lcov.info")
            run("xml", "-o", "coverage.xml")
            results = []
            for report in ("lcov.info", "coverage.xml"):
                out = subprocess.run([sys.executable, str(SCRIPT), "--coverage", report, "--json", "logic.py"],
                                     capture_output=True, text=True, check=True, cwd=work)  # run from the repo root
                results.append({r["function"]: r["crap"] for r in json.loads(out.stdout)["functions"]})
            self.assertEqual(results[0], {"branchy": 4.9, "simple": 2.0})
            self.assertEqual(results[0], results[1])
        finally:
            shutil.rmtree(work)


if __name__ == "__main__":
    unittest.main(verbosity=2)
