"""Verify exercises 10.40–10.59 or analyse a ForeverMart micro/macro dataset."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import scipy
import matplotlib
import base64
import re
from book_answers import load_answers,ANSWER_FILE
from qc.calculations import calculate,integer
from qc.comparison import compare
from qc.simulation import simulate
from qc.reporting import write_report
from qc.scope import assigned_cases, in_assignment, ASSIGNMENT_LABEL, calculation_fingerprint

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', choices=['book','micro','macro'], default='book',
                        help='Book verification (default) or a dataset mini-project')
    data_options=parser.add_mutually_exclusive_group()
    data_options.add_argument('--dataset', type=Path, help='Own CSV for a micro/macro project')
    data_options.add_argument('--synthetic-demo', action='store_true', help='Explicitly use synthetic demonstration data')
    parser.add_argument('--case',action='append',help='Case ID or exercise prefix; repeat to select several')
    parser.add_argument('--input',type=Path,help='Custom JSON: a case object or {cases:[...]}')
    parser.add_argument('--answers',type=Path,default=ANSWER_FILE,help='Explicit independent/printed reference file')
    parser.add_argument('--output',type=Path,default=ROOT/'output')
    parser.add_argument('--trials',type=int,default=100000)
    parser.add_argument('--seed',type=int,default=20260901)
    parser.add_argument('--threshold-ms',type=float,default=None,
                        help='Editable batch-mean response-time target for dataset projects')
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--strict',action='store_true',help='Exit 1 on reference mismatches (not random interval misses)')
    args=parser.parse_args()
    try:
        trials=integer(args.trials,'trials',100); seed=integer(args.seed,'seed',0)
        if args.project!='book':
            from qc.dataset_projects import evaluate_dataset, load_csv
            if args.input or args.case or args.list or args.answers!=ANSWER_FILE:
                raise ValueError('For dataset projects use --dataset CSV; --input, --case, --list and --answers are book options.')
            if trials>100000:
                raise ValueError('Dataset simulation supports at most 100,000 trials.')
            payload=dict(project_type='dataset', scale=args.project,
                         dataset_source='own' if args.dataset else 'demo' if args.synthetic_demo else 'study',
                         trials=trials, seed=seed, specification_ms=args.threshold_ms)
            if args.dataset:
                payload['rows']=load_csv(args.dataset)
            result=evaluate_dataset(payload)
            out=args.output if args.output!=ROOT/'output' else ROOT/'output'/('forevermart-'+args.project)
            out.mkdir(parents=True,exist_ok=True)
            graphdir=out/'graphs'; graphdir.mkdir(exist_ok=True)
            index=0
            def export_plot(match):
                nonlocal index
                index+=1
                name=f'graphs/dataset-{index}.png'
                out.joinpath(name).write_bytes(base64.b64decode(match.group(1)))
                return f'src="{name}"'
            document=re.sub(r'src="data:image/png;base64,([^\"]+)"',export_plot,result['report_html'])
            out.joinpath('report.html').write_text(document,encoding='utf-8')
            out.joinpath('results.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
            print(json.dumps(dict(project=args.project,source=payload['dataset_source'],report=str(out/'report.html')),indent=2))
            return 0
        if args.dataset or args.synthetic_demo:
            raise ValueError('Use --project micro or --project macro with dataset options.')
        path=args.input or ROOT/'data/chapter10_inputs.json'
        data=json.loads(path.read_text(encoding='utf-8'))
        cases=data['cases'] if 'cases' in data else [data]
        if not args.input:
            cases=assigned_cases(cases)
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
                selector=selector.replace('10.','10-',1)
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
            if args.input and args.answers==ANSWER_FILE and (not in_assignment(c['id']) or c['id'] not in original or c['kind']!=original[c['id']]['kind'] or c['inputs']!=original[c['id']]['inputs']):
                ref={}
            case_seed=int.from_bytes(hashlib.sha256((str(seed)+':'+c['id']).encode()).digest()[:8],'big')
            records.append(dict(case=c,calculated=result,comparisons=dict(
                book=compare(result,ref.get('book_reference')),
                independent=compare(result,ref.get('independent_reference'))),
                simulation=simulate(c,result,trials,case_seed),case_seed=case_seed))
        metadata=dict(seed=seed,trials=trials,assignment=ASSIGNMENT_LABEL,engine_sha256=calculation_fingerprint(),
            reference_sha256=hashlib.sha256(args.answers.read_bytes()).hexdigest(),
            input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            versions=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__))
        summary=write_report(records,args.output,metadata)
        print(json.dumps(summary,indent=2))
        return 1 if args.strict and (summary['book_mismatches'] or summary['independent_mismatches']) else 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(f'Input/project error: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
