"""ONE-TIME baseline authoring using math, not the runtime NumPy/SciPy solver.

The resulting JSON is frozen and is never regenerated during a normal run.
Only 'printed_book' entries are transcribed answers; other values are our own
independently solved reference, not a publisher answer key.
"""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cases=json.loads(ROOT.joinpath('data/chapter10_inputs.json').read_text())['cases']
# Independent transcription of the specific table constants needed here.
D2={3:1.693,4:2.059,5:2.326,8:2.847,9:2.970,10:3.078,12:3.258,15:3.472,17:3.588,19:3.689,22:3.819,24:3.895}
R_FACTORS={3:(0,2.574),4:(0,2.282),5:(0,2.114),8:(.136,1.864),9:(.184,1.816),10:(.223,1.777),12:(.283,1.717),15:(.347,1.653),17:(.378,1.622),19:(.403,1.597),22:(.434,1.566),24:(.452,1.548)}
def avg(x): return math.fsum(x)/len(x)
def baseline(case):
    d=case['inputs']; kind=case['kind']
    if kind in ('xbar','range'):
        if 'observations' in d:
            means=[avg(row) for row in d['observations']]; ranges=[max(row)-min(row) for row in d['observations']]
        else: means=d.get('means',[d.get('mean',0)]); ranges=d.get('ranges',[d.get('rbar',0)])
        m=avg(means); r=avg(ranges); n=d['n']
        if kind=='xbar':
            delta=3*d['se'] if 'se' in d else 3*r/(D2[n]*math.sqrt(n))
            return dict(CL=m,LCL=m-delta,UCL=m+delta)
        a,b=R_FACTORS[n]; return dict(CL=r,LCL=a*r,UCL=b*r)
    if kind=='range_identity': return dict(CL=d['rbar'],LCL=d['lcl'],UCL=2*d['rbar']-d['lcl'])
    if kind=='p':
        p=d.get('p')
        if p is None: p=avg(d['proportions']) if 'proportions' in d else avg(d['counts'])/d['n']
        delta=3*math.sqrt(p*(1-p)/d['n'])
        return dict(CL=p,LCL=max(0,p-delta),UCL=min(1,p+delta))
    if kind=='proportion_test':
        p=d['successes']/d['n']; z=(p-d['p0'])/math.sqrt(d['p0']*(1-d['p0'])/d['n'])
        return dict(observed_proportion=p,z=z,p_value=.5*math.erfc(z/math.sqrt(2)))
    if kind=='acceptance':
        n,c,p=d['n'],d['c'],d['p']
        if d.get('model')=='poisson':
            lam=n*p; acceptance=math.exp(-lam)*math.fsum(lam**k/math.factorial(k) for k in range(c+1))
        else: acceptance=math.fsum(math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(c+1))
        return dict(probability=1-acceptance if d['risk']=='producer' else acceptance)
    if kind=='pareto':
        counts=d['counts']; largest=max(counts,key=counts.get)
        return dict(total=sum(counts.values()),largest_count=counts[largest],largest_category=largest)
    raise ValueError(kind)

printed={}
def book(id,values,tolerance,page,note=''):
    printed[id]=dict(values=values,absolute_tolerance=tolerance,printed_page=page,
                    provenance='printed_book',note=note)
for i,(cl,l,u) in enumerate([(26.7,24.9,28.5),(138.6,135.5,141.7),(84.2,77.2,91.2),(8.1,6.9,9.3)]):
    book('SC10-1'+chr(97+i),dict(CL=cl,LCL=l,UCL=u),.051,480 if i<3 else 481)
book('SC10-2',dict(CL=50.417,LCL=49.63,UCL=51.21),.006,481)
for i,(cl,l,u) in enumerate([(5.3,.98,9.62),(15.1,5.71,24.49),(9.6,0,21.91),(7.4,3.21,11.59)]):
    book('SC10-3'+chr(97+i),dict(CL=cl,LCL=l,UCL=u),.006,486)
book('SC10-4',dict(CL=1.367,LCL=0,UCL=2.89),.006,486)
for i,(cl,l,u) in enumerate([(.1,.025,.175),(.9,.784,1),(.36,.231,.489),(.75,.563,.938)]):
    book('SC10-5'+chr(97+i),dict(CL=9 if i==1 else cl,LCL=l,UCL=u),.0006,493 if i<2 else 494,
        'SC10-5(b) prints CL=9 in its worked solution; correct input and probability constraint imply .9. Preserved as an erratum in docs/SOURCE_NOTES.md.' if i==1 else '')
printed['SC10-5b']['known_source_error']=True
book('SC10-6',dict(CL=.898,LCL=.824,UCL=.972),.0006,494,'The answer rounds p to .898 before computing limits; inputs are percentages as printed.')
book('SC10-7',dict(largest_category='Hard disk drive',largest_count=237),0,499,'Chart and text identify hard disk drives and power supplies; Other is last.')
for i,p in enumerate([.1731,.0401,.2642,.0798]):
    book('SC10-8'+chr(97+i),dict(probability=p),.00011,506 if i==0 else 507,
        'Part (c) has an incorrect intermediate subtraction, but its final .2642 is consistent with the correct terms.' if i==2 else '')
for i,p in enumerate([.557,.8095,.4047,.6767]):
    book('SC10-9'+chr(97+i),dict(probability=p),.00011,507 if i<3 else 508)
# Approximate readings visually checked on the printed graphs, NOT printed answer-key numbers.
for ex,values,page in [('10-38',[.13,.46,.72],506),('10-39',[.54,.28,.12],506),
                       ('10-55',[.07,.35,.66],514),('10-56',[.65,.34,.15],514)]:
    for i,p in enumerate(values):
        printed[ex+chr(97+i)]=dict(values={'probability':p},absolute_tolerance=.02,
            printed_page=page,provenance='approximate_graph_reading',note='Visual reading to roughly two decimals; graph appears to use Poisson approximation.')

refs={}
for case in cases:
    refs[case['id']]=dict(independent_reference={'values':baseline(case),'absolute_tolerance':1e-9,
        'provenance':'independently_solved','method':'Python math formulas in tools/build_references.py; frozen before runtime comparison'},
        book_reference=printed.get(case['id']))
ROOT.joinpath('data/chapter10_answers.json').write_text(json.dumps(dict(schema_version=1,references=refs),indent=2),encoding='utf-8')
print(f'Wrote {len(refs)} independent references; {len(printed)} printed/graph references')
