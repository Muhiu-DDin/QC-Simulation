"""Run all exercises, selected cases, or custom input JSON."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import scipy
import matplotlib
from book_answers import load_answers,ANSWER_FILE
from qc.calculations import calculate,integer
from qc.comparison import compare
from qc.simulation import simulate
from qc.reporting import write_report

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',action='append',help='Case ID or exercise prefix; repeat to select several')
    parser.add_argument('--input',type=Path,help='Custom JSON: a case object or {cases:[...]}')
    parser.add_argument('--answers',type=Path,default=ANSWER_FILE,help='Explicit independent/printed reference file')
    parser.add_argument('--output',type=Path,default=ROOT/'output')
    parser.add_argument('--trials',type=int,default=100000)
    parser.add_argument('--seed',type=int,default=20260901)
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--strict',action='store_true',help='Exit 1 on reference mismatches (not random interval misses)')
    args=parser.parse_args()
    try:
        trials=integer(args.trials,'trials',100); seed=integer(args.seed,'seed',0)
        path=args.input or ROOT/'data/chapter10_inputs.json'
        data=json.loads(path.read_text(encoding='utf-8'))
        cases=data['cases'] if 'cases' in data else [data]
        if not cases: raise ValueError('Input contains no cases')
        ids=[c['id'] for c in cases]
        if len(set(ids))!=len(ids): raise ValueError('Case IDs must be unique')
        for id in ids:
            if not isinstance(id,str) or not id or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for ch in id):
                raise ValueError('Case IDs must contain only letters, digits, hyphen or underscore')
        if args.list:
            for c in cases: print(f'{c["id"]:12} {c["kind"]:16} {c["title"]}')
            return 0
        if args.case:
            # Exact IDs win; otherwise select only letter subparts of an exercise.
            selected=[]
            for selector in args.case:
                found=[c for c in cases if c['id']==selector]
                if not found: found=[c for c in cases if c['id'].startswith(selector) and c['id'][len(selector):].isalpha()]
                if not found: raise ValueError(f'Unknown case: {selector}. Use --list.')
                for c in found:
                    if c not in selected: selected.append(c)
            cases=selected
        refs=load_answers(args.answers)
        original={c['id']:c for c in json.loads(ROOT.joinpath('data/chapter10_inputs.json').read_text())['cases']}
        records=[]
        for c in cases:
            result=calculate(c)
            ref=refs.get(c['id'],{})
            # Changed custom inputs must never be compared with the original exercise answer.
            if args.input and args.answers==ANSWER_FILE and (c['id'] not in original or c['kind']!=original[c['id']]['kind'] or c['inputs']!=original[c['id']]['inputs']):
                ref={}
            case_seed=int.from_bytes(hashlib.sha256((str(seed)+':'+c['id']).encode()).digest()[:8],'big')
            records.append(dict(case=c,calculated=result,comparisons=dict(
                book=compare(result,ref.get('book_reference')),
                independent=compare(result,ref.get('independent_reference'))),
                simulation=simulate(c,result,trials,case_seed),case_seed=case_seed))
        metadata=dict(seed=seed,trials=trials,reference_sha256=hashlib.sha256(args.answers.read_bytes()).hexdigest(),
            input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            versions=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__))
        summary=write_report(records,args.output,metadata)
        print(json.dumps(summary,indent=2))
        return 1 if args.strict and (summary['book_mismatches'] or summary['independent_mismatches']) else 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(f'Input/project error: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
