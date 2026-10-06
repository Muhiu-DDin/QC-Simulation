"""Mathematical edge cases, provenance, and complete-catalog verification."""
import json
import unittest
import subprocess
import sys
import tempfile
from pathlib import Path
from qc.calculations import calculate
from qc.comparison import compare
from qc.simulation import simulate
from book_answers import load_answers
ROOT=Path(__file__).resolve().parents[1]

def case(kind,**inputs): return {'id':'test','kind':kind,'inputs':inputs}

class ProjectTests(unittest.TestCase):
    def test_known_standard_error_is_not_divided_twice(self):
        r=calculate(case('xbar',n=12,mean=16.4,se=1.2))
        self.assertAlmostEqual(r['LCL'],12.8); self.assertAlmostEqual(r['UCL'],20)
        self.assertEqual(r['values'],[])  # Summary limits are not raw subgroup observations.

    def test_proportion_limits_and_extremes(self):
        self.assertEqual(calculate(case('p',n=60,p=.9))['UCL'],1)
        self.assertEqual(calculate(case('p',n=82,p=.05))['LCL'],0)
        for p in (0,1):
            r=calculate(case('p',n=20,p=p))
            self.assertEqual(r['CL'],p); self.assertEqual(r['UCL'],p); self.assertEqual(r['LCL'],p)

    def test_without_replacement_is_distinct(self):
        r=calculate(case('acceptance',n=100,c=1,N=1000,p=.02,risk='consumer',model='binomial'))
        self.assertAlmostEqual(r['probability'],.403271710782,places=10)
        self.assertAlmostEqual(r['finite_lot_probability'],.389154,places=5)
        self.assertGreater(r['probability'],r['finite_lot_probability'])

    def test_noninteger_lot_is_never_silently_rounded(self):
        r=calculate(case('acceptance',n=250,c=2,N=2500,p=.015,risk='consumer',model='binomial'))
        self.assertNotIn('finite_lot_probability',r)
        self.assertIn('finite_lot_note',r)

    def test_no_outliers_can_still_signal_shift(self):
        r=calculate(case('p',n=10,p=.5,proportions=[.6]*8))
        self.assertFalse(r['above_UCL']); self.assertTrue(r['pattern_signals'])

    def test_raw_rows_determine_mean_and_range(self):
        r=calculate(case('xbar',n=3,observations=[[1,2,3],[4,5,6]]))
        self.assertEqual(r['grand_mean'],3.5); self.assertEqual(r['Rbar'],2)

    def test_validation(self):
        invalid=[case('p',n=0,p=.1),case('p',n=10,p=1.1),case('p',n=10,counts=[1.5]),
                 case('xbar',n=3,observations=[[1,2]]),case('xbar',n=30,mean=0,rbar=1),
                 case('acceptance',n=100,c=101,N=1000,p=.1,risk='consumer'),
                 case('range_identity',rbar=6,lcl=0),case('pareto',counts={'A':0}),
                 case('xbar',n=5,mean=1),case('range',n=5)]
        for c in invalid:
            with self.subTest(c=c), self.assertRaises(ValueError): calculate(c)

    def test_references_and_complete_coverage(self):
        cases=json.loads(ROOT.joinpath('data/chapter10_inputs.json').read_text())['cases']
        refs=load_answers(); self.assertEqual(len(cases),len(refs))
        for c in cases:
            r=calculate(c); reference=refs[c['id']]
            with self.subTest(id=c['id']):
                self.assertEqual(compare(r,reference['independent_reference'])['status'],'MATCH')
                status=compare(r,reference['book_reference'])['status']
                self.assertIn(status,('MATCH','NO_BOOK_ANSWER','SOURCE_ERRATUM'))
        self.assertEqual(refs['SC10-5b']['book_reference']['values']['CL'],9)
        self.assertEqual(compare(calculate(next(c for c in cases if c['id']=='SC10-5b')),refs['SC10-5b']['book_reference'])['status'],'SOURCE_ERRATUM')

    def test_seeded_simulation(self):
        c=case('acceptance',n=100,c=1,N=1000,p=.02,risk='consumer',model='binomial'); r=calculate(c)
        a=simulate(c,r,10000,123); b=simulate(c,r,10000,123)
        self.assertEqual(a,b); self.assertLess(a['primary']['absolute_error'],.03)

    def test_missing_reference_and_rounding(self):
        self.assertEqual(compare({},None)['status'],'NO_BOOK_ANSWER')
        ref=dict(values={'x':.563},absolute_tolerance=.0006,provenance='printed_book')
        self.assertEqual(compare({'x':.5625},ref)['status'],'MATCH')
        self.assertEqual(compare({'x':.56},ref)['status'],'MISMATCH')

    def test_custom_inputs_do_not_use_old_exercise_answer(self):
        ROOT.joinpath('tmp').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as directory:
            path=Path(directory); custom=case('p',n=144,p=.2)
            custom.update(id='SC10-5a',title='Changed input')
            source=path/'input.json'; source.write_text(json.dumps(custom))
            run=subprocess.run([sys.executable,str(ROOT/'run.py'),'--input',str(source),'--output',str(path/'report'),'--trials','100','--strict'],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            rec=json.loads(path.joinpath('report/results.json').read_text())['records'][0]
            self.assertEqual(rec['calculated']['CL'],.2)
            self.assertEqual(rec['comparisons']['book']['status'],'NO_BOOK_ANSWER')
            self.assertEqual(rec['comparisons']['independent']['fields'],[])

    def test_cli_unknown_case_is_rejected(self):
        run=subprocess.run([sys.executable,str(ROOT/'run.py'),'--case','does-not-exist'],capture_output=True,text=True)
        self.assertEqual(run.returncode,2); self.assertIn('Unknown case',run.stderr)

if __name__=='__main__': unittest.main()
