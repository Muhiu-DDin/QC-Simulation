"""Shared online calculator, using the same formulas and references as the CLI."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import threading
from .calculations import calculate, integer
from .comparison import compare
from .simulation import simulate
from .reporting import plot_case
from .report_ui import render_report

ROOT=Path(__file__).resolve().parents[1]
PLOT_LOCK=threading.Lock()

def catalog():
    return json.loads(ROOT.joinpath('data/chapter10_inputs.json').read_text(encoding='utf-8'))['cases']

def signature(kind,inputs):
    cleaned={k:v for k,v in inputs.items() if k not in ('unit','attribute','labels')}
    if kind=='range': cleaned.pop('mean',None)
    if kind=='acceptance': cleaned.setdefault('model','binomial')
    if kind=='proportion_test': cleaned.setdefault('alpha',.05)
    return kind,cleaned

def evaluate(payload):
    if not isinstance(payload,dict): raise ValueError('Please provide a calculation object.')
    kind=payload.get('kind'); inputs=payload.get('inputs')
    if not isinstance(inputs,dict): raise ValueError('Input values are required.')
    if len(json.dumps(inputs))>100000: raise ValueError('Please use a smaller dataset.')
    trials=integer(payload.get('trials',10000),'Simulation trials',100)
    if trials>100000: raise ValueError('Use at most 100,000 simulation trials online.')
    if 'n' in inputs:
        n=integer(inputs['n'],'Sample size')
        if n>(1000000 if kind=='proportion_test' else 10000): raise ValueError('Sample size is too large for an online calculation.')
    if kind=='acceptance' and integer(inputs['N'],'Lot size')>1000000000:
        raise ValueError('Lot size must not exceed one billion.')
    for key in ('observations','means','ranges','counts','proportions'):
        if isinstance(inputs.get(key),list) and len(inputs[key])>1000: raise ValueError('Use at most 1,000 subgroups online.')
    case={'id':'custom-input','kind':kind,'title':'Independent calculation','inputs':inputs}
    result=calculate(case)
    matches=[c for c in catalog() if signature(c['kind'],c['inputs'])==signature(kind,inputs)]
    selected=next((c for c in matches if c['id']==payload.get('exercise_id')),matches[0] if matches else None)
    if payload.get('data_source')=='own':
        selected=None
    elif payload.get('data_source')=='book':
        selected=next((c for c in catalog() if c['id']==payload.get('exercise_id') and c['kind']==kind),None)
        if selected is None: raise ValueError('Select a book question for this calculation type.')
    refs=json.loads(ROOT.joinpath('data/chapter10_answers.json').read_text(encoding='utf-8'))['references']
    if selected:
        case={**selected,'inputs':inputs}
        reference=refs[selected['id']]
        message=f"These values match stored exercise {selected['id']}. Available reference answers are compared below."
        if selected not in matches:
            message=f"Compared with selected exercise {selected['id']}. Your inputs differ from the book inputs; differences in answers are expected."
        category='book'
    else:
        reference={}
        message='Independent data: these input values do not match a stored Chapter 10 exercise. Results are calculated from the formulas; no textbook answer comparison is available.'
        if payload.get('data_source')=='own':
            message='Independent data: calculated using your own values. No textbook answer comparison is performed.'
        category='independent'
    seed=20260901
    case_seed=int.from_bytes(hashlib.sha256((str(seed)+':'+case['id']).encode()).digest()[:8],'big')
    simulation=simulate(case,result,trials,case_seed)
    record=dict(case=case,calculated=result,comparisons=dict(book=compare(result,reference.get('book_reference')),
        independent=compare(result,reference.get('independent_reference'))),simulation=simulation,case_seed=case_seed)
    with PLOT_LOCK, tempfile.TemporaryDirectory() as directory:
        plot=plot_case(case,result,Path(directory))
        url='data:image/png;base64,'+base64.b64encode(Path(directory,Path(plot).name).read_bytes()).decode() if plot else None
    document=render_report([record],dict(seed=seed,trials=trials),{case['id']:url})
    # Embedded result pages have no file downloads; use the application's JSON export.
    import re
    document=re.sub(r'<a[^>]*href="(?:comparison.csv|results.json)"[^>]*>.*?</a>','',document)
    document=document.replace('Export comparisons ↓','')
    return dict(category=category,message=message,matched_exercises=[c['id'] for c in matches],
                record=record,report_html=document)
