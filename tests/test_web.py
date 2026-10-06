import unittest
from qc.web_service import evaluate,catalog

class WebCalculatorTests(unittest.TestCase):
    def test_explicit_book_selection_compares_changed_values(self):
        result=evaluate(dict(kind='xbar',data_source='book',exercise_id='SC10-1a',inputs=dict(n=9,mean=30,rbar=6),trials=100))
        self.assertEqual(result['category'],'book')
        self.assertEqual(result['record']['case']['id'],'SC10-1a')
        self.assertEqual(result['record']['comparisons']['book']['status'],'MISMATCH')
        self.assertIn('inputs differ',result['message'])

    def test_own_mode_disables_comparison_even_for_book_values(self):
        result=evaluate(dict(kind='xbar',data_source='own',exercise_id='SC10-1a',inputs=dict(n=9,mean=26.7,rbar=5.3),trials=100))
        self.assertEqual(result['category'],'independent')
        self.assertEqual(result['record']['comparisons']['book']['fields'],[])

    def test_book_mode_requires_valid_question(self):
        with self.assertRaises(ValueError):
            evaluate(dict(kind='xbar',data_source='book',inputs=dict(n=9,mean=30,rbar=6),trials=100))

    def test_book_inputs_match_without_exercise_id(self):
        result=evaluate(dict(kind='xbar',inputs=dict(n=9,mean=26.7,rbar=5.3),trials=100))
        self.assertEqual(result['category'],'book')
        self.assertIn('SC10-1a',result['matched_exercises'])
        self.assertEqual(result['record']['comparisons']['book']['status'],'MATCH')
        self.assertIn('data:image/png;base64,',result['report_html'])

    def test_custom_inputs_never_use_selected_book_reference(self):
        result=evaluate(dict(kind='xbar',exercise_id='SC10-1a',inputs=dict(n=9,mean=30,rbar=6),trials=100))
        self.assertEqual(result['category'],'independent')
        self.assertEqual(result['matched_exercises'],[])
        self.assertEqual(result['record']['comparisons']['book']['fields'],[])
        self.assertAlmostEqual(result['record']['calculated']['UCL'],32.0202020202)
        self.assertIn('Independent data',result['message'])

    def test_all_seven_types_accept_stored_data(self):
        for kind in ['xbar','range','p','acceptance','pareto','proportion_test','range_identity']:
            case=next(c for c in catalog() if c['kind']==kind)
            with self.subTest(kind=kind):
                response=evaluate(dict(kind=kind,exercise_id=case['id'],inputs=case['inputs'],trials=100))
                self.assertEqual(response['category'],'book')
                self.assertIn(case['id'],response['matched_exercises'])
                self.assertEqual(response['record']['comparisons']['independent']['status'],'MATCH')

    def test_invalid_values_and_online_limits(self):
        for payload in [dict(kind='p',inputs=dict(n=100,p=3)),dict(kind='xbar',inputs=dict(n=9,mean=30,rbar=6),trials=100001)]:
            with self.assertRaises(ValueError): evaluate(payload)

    def test_cosmetic_metadata_does_not_block_matching(self):
        response=evaluate(dict(kind='range',inputs=dict(n=9,rbar=5.3,unit='units'),trials=100))
        self.assertEqual(response['category'],'book')
        self.assertIn('SC10-3a',response['matched_exercises'])

if __name__=='__main__': unittest.main()
