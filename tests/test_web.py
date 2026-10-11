"""Assigned-scope book selection and independent website dataset requests."""
import unittest
from qc.web_service import evaluate, catalog
from qc.scope import assignment_manifest, in_assignment


class WebCalculatorTests(unittest.TestCase):
    def test_only_assigned_book_cases_are_available(self):
        cases=catalog()
        self.assertEqual(len(cases),22)
        self.assertTrue(all(in_assignment(c['id']) for c in cases))
        self.assertEqual({c['id'] for c in cases},
                         {id for q in assignment_manifest()['exercises'] for id in q['case_ids']})

    def test_explicit_book_selection_compares_changed_values(self):
        result=evaluate(dict(kind='xbar',data_source='book',exercise_id='10-44',
                             inputs=dict(n=10,mean=30,rbar=6),trials=100))
        self.assertEqual(result['category'],'book')
        self.assertEqual(result['record']['case']['id'],'10-44')
        self.assertEqual(result['record']['comparisons']['independent']['status'],'MISMATCH')
        self.assertIn('inputs differ',result['message'])

    def test_own_mode_disables_comparison_even_for_book_values(self):
        c=catalog()[0]
        result=evaluate(dict(kind=c['kind'],data_source='own',exercise_id=c['id'],inputs=c['inputs'],trials=100))
        self.assertEqual(result['category'],'independent')
        self.assertEqual(result['record']['comparisons']['book']['fields'],[])
        self.assertEqual(result['record']['comparisons']['independent']['fields'],[])

    def test_book_mode_rejects_unassigned_or_missing_question(self):
        for id in ('','SC10-1a','10-39a','10-60'):
            with self.subTest(id=id), self.assertRaises(ValueError):
                evaluate(dict(kind='xbar',data_source='book',exercise_id=id,
                              inputs=dict(n=9,mean=30,rbar=6),trials=100))

    def test_book_inputs_match_without_exercise_id(self):
        c=next(c for c in catalog() if c['id']=='10-44')
        result=evaluate(dict(kind=c['kind'],inputs=c['inputs'],trials=100))
        self.assertEqual(result['category'],'book')
        self.assertIn(c['id'],result['matched_exercises'])
        self.assertEqual(result['record']['comparisons']['independent']['status'],'MATCH')
        self.assertEqual(result['record']['comparisons']['book']['status'],'NO_BOOK_ANSWER')
        self.assertIn('data:image/png;base64,',result['report_html'])

    def test_custom_inputs_without_book_mode_never_use_selected_reference(self):
        result=evaluate(dict(kind='xbar',exercise_id='10-44',inputs=dict(n=9,mean=30,rbar=6),trials=100))
        self.assertEqual(result['category'],'independent')
        self.assertEqual(result['matched_exercises'],[])
        self.assertEqual(result['record']['comparisons']['book']['fields'],[])
        self.assertAlmostEqual(result['record']['calculated']['UCL'],32.0202020202)

    def test_every_assigned_kind_accepts_stored_data(self):
        for kind in {c['kind'] for c in catalog()}:
            c=next(c for c in catalog() if c['kind']==kind)
            with self.subTest(kind=kind):
                result=evaluate(dict(kind=kind,data_source='book',exercise_id=c['id'],inputs=c['inputs'],trials=100))
                self.assertEqual(result['category'],'book')
                self.assertEqual(result['record']['comparisons']['independent']['status'],'MATCH')

    def test_invalid_values_and_online_limits(self):
        for payload in [dict(kind='p',inputs=dict(n=100,p=3)),
                        dict(kind='xbar',inputs=dict(n=9,mean=30,rbar=6),trials=100001)]:
            with self.assertRaises(ValueError): evaluate(payload)

    def test_cosmetic_metadata_does_not_block_matching(self):
        c=next(c for c in catalog() if c['id']=='10-45')
        result=evaluate(dict(kind='range',inputs={**c['inputs'],'unit':'seconds'},trials=100))
        self.assertEqual(result['category'],'book')
        self.assertIn('10-45',result['matched_exercises'])

    def test_dataset_dispatch_has_no_book_comparison(self):
        result=evaluate(dict(project_type='dataset',scale='micro',dataset_source='own',trials=100,
                             rows=[dict(period='sample',passed=9,failed=1,response_ms=120)]))
        self.assertEqual(result['category'],'independent')
        self.assertEqual(result['matched_exercises'],[])
        self.assertEqual(result['record']['comparisons']['book']['fields'],[])


if __name__=='__main__': unittest.main()
