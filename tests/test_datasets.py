"""Tests for independent dataset aggregation and seeded model verification."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy import stats

from qc.dataset_projects import (evaluate_dataset, generate_demo, load_csv,
                                 validate_rows, _groups, _simulate)


class DatasetProjectTests(unittest.TestCase):
    def calculate(self, rows, **kwargs):
        with patch("qc.dataset_projects._plots", return_value={"failure_chart": "data:image/png;base64,", "timing_chart": "data:image/png;base64,"}):
            return evaluate_dataset({**dict(project_type="dataset", scale="micro", dataset_source="own",
                                           rows=rows, trials=1000), **kwargs})

    def test_unequal_batch_sizes_use_pooled_counts_and_variable_limits(self):
        rows = [dict(period="large", passed=90, failed=10, response_ms=600),
                dict(period="small", passed=1, failed=1, response_ms=200)]
        response = self.calculate(rows)
        summary = response["record"]["calculated"]
        self.assertAlmostEqual(summary["failure_rate"], 11 / 102)
        self.assertNotAlmostEqual(summary["failure_rate"], (.1 + .5) / 2)
        self.assertAlmostEqual(summary["weighted_mean_response_ms"], 60400 / 102)
        first, last = summary["first_batch_limits"], summary["last_batch_limits"]
        self.assertGreater(first["LCL"], 0)
        self.assertEqual(last["LCL"], 0)
        self.assertGreater(last["UCL"], first["UCL"])
        self.assertEqual(response["matched_exercises"], [])
        self.assertEqual(response["record"]["comparisons"]["book"]["status"], "NOT_AVAILABLE")
        self.assertIn("No textbook answer comparison", response["message"])
        json.dumps(response, allow_nan=False)

    def test_grouped_chart_uses_total_failures_and_execution_weighting(self):
        rows = [dict(period=str(i), passed=9, failed=1, response_ms=100) for i in range(121)]
        rows[1] = dict(period="1", passed=990, failed=10, response_ms=900)
        groups = _groups(rows, 130 / 2200)
        first = groups[0]
        self.assertEqual(first["batches"], 2)
        self.assertEqual(first["executions"], 1010)
        self.assertAlmostEqual(first["failure_rate"], 11 / 1010)
        self.assertAlmostEqual(first["response_ms"], (1000 + 900000) / 1010)
        self.assertEqual(sum(group["executions"] for group in groups), 2200)
        self.assertEqual(sum(group["failed"] for group in groups), 130)
        self.assertEqual(groups[-1]["last_row"], 121)

    def test_zero_failure_boundary_is_not_claimed_as_zero_true_risk(self):
        rows = [dict(period="a", passed=15, failed=0, response_ms=100),
                dict(period="b", passed=15, failed=0, response_ms=300)]
        response = self.calculate(rows)
        summary = response["record"]["calculated"]
        simulation = response["record"]["simulation"]
        self.assertEqual(summary["failure_rate"], 0)
        self.assertEqual(summary["failure_ci95_low"], 0)
        self.assertGreater(summary["failure_ci95_high"], 0)
        self.assertEqual(simulation["exact_outside_probability"], 0)
        self.assertEqual(simulation["simulated_outside_probability"], 0)
        self.assertTrue(simulation["exact_within_ci99"])
        self.assertEqual(simulation["timing_resampling"]["target_weighted_mean_ms"], 200)
        self.assertIn("does not show that the website can never fail", response["report_html"])
        self.assertIn("not a population confidence interval", response["report_html"])

    def test_all_failure_boundary_remains_failure_and_clips_to_one(self):
        response = self.calculate([dict(period="a", passed=0, failed=4, response_ms=350)])
        summary = response["record"]["calculated"]
        self.assertEqual(summary["failure_rate"], 1)
        self.assertEqual(summary["first_batch_limits"], dict(LCL=1., CL=1., UCL=1.))
        self.assertEqual(summary["failure_ci95_high"], 1)
        self.assertIn("does not mean acceptable quality", response["report_html"])

    def test_exact_binomial_tail_matches_exhaustive_discrete_distribution(self):
        simulation = _simulate(.21, 27, 1000, 20260901)
        outcomes = np.arange(28)
        outside = (outcomes / 27 < simulation["LCL"]) | (outcomes / 27 > simulation["UCL"])
        exact = stats.binom.pmf(outcomes, 27, .21)[outside].sum()
        self.assertAlmostEqual(simulation["exact_outside_probability"], float(exact), places=12)

    def test_seeded_simulations_are_reproducible(self):
        rows = [dict(period="a", passed=18, failed=2, response_ms=120),
                dict(period="b", passed=85, failed=15, response_ms=350)]
        self.assertEqual(self.calculate(rows)["record"]["simulation"],
                         self.calculate(rows)["record"]["simulation"])

    def test_csv_numeric_rows_and_header_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "sample.csv")
            path.write_text("period,passed,failed,response_ms\na,5,1,120.5\nb,15,0,200\n", encoding="utf-8")
            self.assertEqual(load_csv(path)[0]["failed"], 1)
            self.assertEqual(load_csv(path)[0]["response_ms"], 120.5)
            for text in ["period,passed,failed\na,5,1\n", "period,passed,failed,response_ms\na,5,1,2,3\n",
                         "period,passed,failed,response_ms\na,5,,120\n",
                         "period,passed,failed,response_ms\na,5,1,NaN\n",
                         "period,passed,failed,response_ms\na,5,1,-2\n"]:
                path.write_text(text, encoding="utf-8")
                with self.subTest(text=text), self.assertRaises(ValueError):
                    load_csv(path)

    def test_bad_counts_and_dataset_limits_are_rejected(self):
        good = dict(period="a", passed=5, failed=1, response_ms=100)
        for change in [dict(passed=-1), dict(failed=1.5), dict(response_ms=0),
                       dict(response_ms=float("inf")), dict(passed=True), dict(passed=0, failed=0),
                       dict(period=""), dict(passed=1e10)]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_rows([{**good, **change}])
        for rows in [[], None, [good, good], [good] * 20001]:
            with self.assertRaises(ValueError):
                validate_rows(rows)
        for settings in [dict(trials=99), dict(trials=100001), dict(specification_ms="nan"), dict(seed=-1)]:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.calculate([good], **settings)

    def test_demo_data_are_deterministic_and_explicitly_labelled(self):
        self.assertEqual(generate_demo("micro"), generate_demo("micro"))
        self.assertEqual(len(generate_demo("micro")), 30)
        self.assertEqual(len(generate_demo("macro")), 10000)
        with patch("qc.dataset_projects._plots", return_value={"failure_chart": "", "timing_chart": ""}):
            response = evaluate_dataset(dict(dataset_source="demo", scale="micro", trials=100))
        self.assertIn("synthetic", response["message"])
        self.assertIn("not collected website measurements", response["message"])
        self.assertEqual(response["record"]["case"]["inputs"]["dataset_source"], "demo")

    def test_recorded_website_source_is_default_and_displays_collection_definition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            data.mkdir()
            (data / "forevermart_micro.csv").write_text("period,passed,failed,response_ms\na,3,0,215.2\nb,3,0,220.8\n", encoding="utf-8")
            (data / "forevermart_dataset_manifest.json").write_text(json.dumps(dict(
                source_url="https://forevermart.vercel.app/", captured_at_utc="2026-10-11T12:00:00Z",
                check_definition="HTTP 200 and a React root", synthetic=False,
                scales={"micro": {"routes": ["/"]}})), encoding="utf-8")
            with patch("qc.dataset_projects.ROOT", root), patch("qc.dataset_projects._plots", return_value={"failure_chart": "", "timing_chart": ""}):
                response = evaluate_dataset(dict(scale="micro", trials=100))
            self.assertEqual(response["record"]["case"]["inputs"]["dataset_source"], "forevermart")
            self.assertEqual(response["record"]["calculated"]["total_executions"], 6)
            self.assertFalse(response["record"]["provenance"]["synthetic"])
            self.assertIn("HTTP 200 and a React root", response["report_html"])
            self.assertIn("2026-10-11T12:00:00Z", response["report_html"])


if __name__ == "__main__":
    unittest.main()
