"""Verify the PDF study against full-precision source evidence and its frozen answers."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qc.dataset_projects import evaluate_dataset, load_csv
from qc.study_projects import (load_study, bootstrap_groups, micro_analysis,
                               validate_micro_rows, STUDY)


class PDFStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis, cls.raw, cls.catalog, cls.reference, cls.matches = load_study()

    def calculate(self, scale='micro', **kwargs):
        with patch('qc.study_projects.study_plots', return_value={'bootstrap': ('Simulation', 'data:image/png;base64,iVBORw0KGgo=')}):
            return evaluate_dataset({'scale': scale, 'trials': 1000, **kwargs})

    def test_all_original_results_match_the_separately_frozen_reference(self):
        self.assertTrue(all(self.matches.values()), self.matches)
        self.assertEqual(len(self.raw), 225)
        self.assertEqual(self.analysis['micro']['count'], 125)
        self.assertEqual(self.analysis['macro']['attempts'], 100)
        self.assertEqual(self.analysis['catalog']['count'], 40)
        self.assertEqual(self.analysis['ui']['count'], 15)
        self.assertEqual(self.analysis['ui']['failed'], 2)

    def test_micro_limits_and_flags_agree_with_the_pdf(self):
        result = self.analysis['micro']
        self.assertEqual(round(result['mean_ms'], 2), 683.42)
        self.assertEqual(round(result['p95_ms'], 2), 774.71)
        self.assertEqual(round(result['p99_ms'], 2), 1033.05)
        self.assertEqual(round(result['limits']['xbar_lcl'], 2), 618.65)
        self.assertEqual(round(result['limits']['xbar_ucl'], 2), 748.18)
        self.assertEqual(round(result['limits']['range_ucl'], 2), 237.37)
        self.assertEqual(result['mean_signals'], [13, 14])
        self.assertEqual(result['range_signals'], [1, 3, 12, 13])
        self.assertEqual(result['tukey_outliers'], 14)

    def test_raw_micro_recalculation_matches_full_precision_not_rounded_means(self):
        rows = [dict(period=str(g['batch']), **{f't{i}_ms': g[f't{i}_ms'] for i in range(1, 6)})
                for g in self.analysis['micro_groups']]
        actual, groups, values = micro_analysis(rows)
        for field in ['mean_ms', 'p95_ms', 'p99_ms', 'sample_sd_ms', 'halfwidth_d2_ms']:
            self.assertAlmostEqual(actual[field], self.analysis['micro'][field], places=10)
        self.assertEqual(actual['mean_signals'], [13, 14])
        self.assertEqual(values.shape, (25, 5))
        self.assertNotEqual(values[0, 0], round(values[0, 0], 2))

    def test_expected_401_is_a_pass_and_browser_issues_do_not_pollute_service_counts(self):
        checks = [r for r in self.raw if r['feature'] == 'Anonymous access protection']
        self.assertEqual(len(checks), 20)
        self.assertTrue(all(r['http_status'] == '401' and r['passed'] == 'True' for r in checks))
        result = self.calculate('macro')
        self.assertEqual(result['record']['calculated']['failures'], 0)
        self.assertEqual(result['record']['calculated']['attempts'], 100)
        self.assertEqual(result['record']['ui']['failed'], 2)
        self.assertIn('401 is a <strong>pass</strong>', result['report_html'])
        self.assertIn('data:image/jpeg;base64,', result['report_html'])

    def test_default_source_is_pdf_study_and_optional_target_is_not_invented(self):
        result = self.calculate()
        record = result['record']
        self.assertEqual(record['case']['inputs']['dataset_source'], 'study')
        self.assertIsNone(record['case']['inputs']['specification_ms'])
        self.assertIsNone(record['target_exceedance_count'])
        self.assertEqual(record['comparisons']['pdf_study']['status'], 'Verified')
        self.assertEqual(record['comparisons']['book']['status'], 'NOT_AVAILABLE')
        self.assertTrue(record['provenance']['no_new_network_requests'])
        self.assertIn('7 October 2026', result['message'])
        json.dumps(result, allow_nan=False)

    def test_bootstrap_resamples_whole_groups_and_reproduces_example_mean(self):
        values = np.array([[g[f't{i}_ms'] for i in range(1, 6)] for g in self.analysis['micro_groups']])
        result, draws = bootstrap_groups(values, 1000, 123, micro=True)
        indices = np.array(result['example_selected_groups'])-1
        self.assertEqual(len(indices), 25)
        self.assertLess(len(set(indices)), len(indices))
        self.assertAlmostEqual(float(values[indices].mean()), result['example_trial_mean_ms'])
        self.assertAlmostEqual(float(draws.mean()), result['simulated_mean_ms'])
        self.assertEqual(result['exploratory_ci95_low_ms'], float(np.percentile(draws, 2.5)))
        self.assertEqual(result['exploratory_ci95_high_ms'], float(np.percentile(draws, 97.5)))
        self.assertAlmostEqual(result['mean_mc_standard_error_ms'], draws.std(ddof=1)/np.sqrt(1000))
        self.assertIn('control_limit_sensitivity', result)

    def test_fixed_seed_repeats_simulation_and_changed_seed_does_not_change_observations(self):
        first, repeat, changed = self.calculate(seed=123), self.calculate(seed=123), self.calculate(seed=124)
        self.assertEqual(first['record']['simulation'], repeat['record']['simulation'])
        self.assertNotEqual(first['record']['simulation'], changed['record']['simulation'])
        self.assertEqual(first['record']['calculated'], changed['record']['calculated'])

    def test_macro_simulation_zero_failure_boundary_is_reported_honestly(self):
        result = self.calculate('macro')['record']
        model = result['simulation']['failure_model']
        self.assertEqual(model['representative_batch_size'], 5)
        self.assertEqual(model['exact_outside_probability'], 0)
        self.assertEqual(model['outside_events'], 0)
        self.assertGreater(result['calculated']['wilson_95_interval'][1], .03)
        bootstrap = result['simulation']['group_bootstrap']
        self.assertEqual(bootstrap['groups_per_trial'], 20)
        self.assertGreater(bootstrap['exploratory_ci95_high_ms'], bootstrap['exploratory_ci95_low_ms'])

    def test_modified_evidence_is_detected_instead_of_comparison_being_forced(self):
        with tempfile.TemporaryDirectory() as directory:
            from shutil import copytree
            target = Path(directory)/'study'
            copytree(STUDY, target)
            source = target/'requests.csv'
            source.write_text(source.read_text(encoding='utf-8').replace('657.4280000058934', '600.0'), encoding='utf-8')
            with patch('qc.study_projects.STUDY', target), self.assertRaisesRegex(ValueError, 'evidence has changed'):
                load_study()

    def test_own_raw_micro_csv_is_independent_and_preserves_individual_values(self):
        csv = 'period,t1_ms,t2_ms,t3_ms,t4_ms,t5_ms\n' + ''.join(f'{i},100,200,300,400,{500+i}\n' for i in range(5))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'raw.csv'
            path.write_text(csv, encoding='utf-8')
            rows = load_csv(path)
        result = self.calculate(dataset_source='own', rows=rows, specification_ms=400)
        self.assertEqual(result['record']['calculated']['count'], 25)
        self.assertAlmostEqual(result['record']['calculated']['mean_ms'], 300.4)
        self.assertEqual(result['record']['target_exceedance_count'], 5)
        self.assertEqual(result['record']['comparisons']['pdf_study']['status'], 'NOT_AVAILABLE')
        self.assertNotIn('catalog', result['record'])
        self.assertIn('your own observations', result['message'])
        with self.assertRaisesRegex(ValueError, 'micro studies only'):
            self.calculate('macro', dataset_source='own', rows=rows)

    def test_invalid_raw_inputs_and_settings_are_rejected(self):
        rows = [dict(period=str(i), t1_ms=100, t2_ms=200, t3_ms=300, t4_ms=400, t5_ms=500) for i in range(5)]
        for change in [dict(t1_ms=0), dict(t1_ms=True), dict(t1_ms=float('nan')), dict(period=''), dict(t6_ms=20)]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_micro_rows([{**rows[0], **change}, *rows[1:]])
        for bad in [rows[:4], rows*101]:
            with self.assertRaises(ValueError):
                validate_micro_rows(bad)
        for change in [dict(seed=-1), dict(seed=True), dict(trials=99), dict(specification_ms=0)]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.calculate(**change)


if __name__ == '__main__':
    unittest.main()
