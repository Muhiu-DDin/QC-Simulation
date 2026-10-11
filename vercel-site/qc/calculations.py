"""Independent runtime calculations using NumPy and SciPy.

Control-chart factors are transcribed from Appendix Table 9, printed p.972.
Xbar limits use d2 directly; R limits use the printed D3/D4 factors.
"""
import math
import numpy as np
from scipy import stats

# n: (d2, d3, D3, D4)
FACTORS = {
    2:(1.128,.853,0,3.269),3:(1.693,.888,0,2.574),4:(2.059,.880,0,2.282),
    5:(2.326,.864,0,2.114),6:(2.534,.848,0,2.004),7:(2.704,.833,.076,1.924),
    8:(2.847,.820,.136,1.864),9:(2.970,.808,.184,1.816),10:(3.078,.797,.223,1.777),
    11:(3.173,.787,.256,1.744),12:(3.258,.779,.283,1.717),13:(3.336,.770,.308,1.692),
    14:(3.407,.763,.328,1.672),15:(3.472,.756,.347,1.653),16:(3.532,.750,.363,1.637),
    17:(3.588,.744,.378,1.622),18:(3.640,.739,.391,1.609),19:(3.689,.734,.403,1.597),
    20:(3.735,.729,.414,1.586),21:(3.778,.724,.425,1.575),22:(3.819,.720,.434,1.566),
    23:(3.858,.716,.443,1.557),24:(3.895,.712,.452,1.548),25:(3.931,.708,.460,1.540)}

def integer(value, label, minimum=1):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or int(value)!=value or value<minimum:
        raise ValueError(f'{label} must be an integer >= {minimum}')
    return int(value)

def number(value,label,minimum=None,maximum=None):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number')
    value=float(value)
    if minimum is not None and value<minimum or maximum is not None and value>maximum:
        raise ValueError(f'{label} must be in [{minimum}, {maximum}]')
    return value

def vector(values,label,lo=None,hi=None):
    if not isinstance(values,list) or not values:
        raise ValueError(f'{label} must be a nonempty list')
    return np.array([number(v,label,lo,hi) for v in values])

def pattern_signals(values,cl):
    """Explicit supplementary rules: 8 on one side; 6 strictly monotonic.

    These are project diagnostics, not claimed to be rules specified by the book.
    Cycling and changes in spread still need human interpretation.
    """
    v=np.asarray(values)
    signals=[]
    for width,rule in [(8,'eight on one side'),(6,'six strictly increasing/decreasing')]:
        for start in range(len(v)-width+1):
            w=v[start:start+width]
            hit=(np.all(w>cl) or np.all(w<cl)) if width==8 else (np.all(np.diff(w)>0) or np.all(np.diff(w)<0))
            if hit: signals.append({'rule':rule,'start':start+1,'end':start+width})
    return signals

def chart_result(cl,lcl,ucl,values,**extra):
    v=np.asarray(values,dtype=float)
    return dict(CL=float(cl),LCL=float(lcl),UCL=float(ucl),values=v.tolist(),
                below_LCL=(np.flatnonzero(v<lcl)+1).tolist(),above_UCL=(np.flatnonzero(v>ucl)+1).tolist(),
                pattern_signals=pattern_signals(v,cl),**extra)

def calculate(case):
    kind=case['kind']; d=case['inputs']
    if kind in ('xbar','range'):
        n=integer(d['n'],'n')
        if 'observations' in d:
            raw=d['observations']
            if not isinstance(raw,list) or not raw: raise ValueError('observations cannot be empty')
            obs=np.array([vector(row,'observations') for row in raw])
            if obs.ndim!=2 or obs.shape[1]!=n: raise ValueError('Each subgroup must have n observations')
            means=obs.mean(axis=1); ranges=np.ptp(obs,axis=1)
        elif 'means' in d or 'ranges' in d:
            means=vector(d['means'],'means'); ranges=vector(d['ranges'],'ranges',0)
            if len(means)!=len(ranges): raise ValueError('means and ranges lengths must match')
        else:
            if kind=='xbar' and 'mean' not in d:
                raise ValueError('Scalar xbar input requires mean')
            if 'rbar' not in d and not (kind=='xbar' and 'se' in d):
                raise ValueError('Provide observations, means/ranges, rbar, or a known xbar standard error')
            means=np.array([number(d.get('mean',0),'mean')]); ranges=np.array([number(d.get('rbar',0),'rbar',0)])
        m=float(means.mean()); r=float(ranges.mean())
        observed_subgroups='observations' in d or 'means' in d
        if 'labels' in d and (not isinstance(d['labels'],list) or len(d['labels'])!=len(means)):
            raise ValueError('labels must have one entry per subgroup')
        if 'se' in d and kind=='xbar': se=number(d['se'],'se',0)
        else:
            if n not in FACTORS: raise ValueError('Appendix factors support subgroup n=2..25')
            se=r/FACTORS[n][0]/math.sqrt(n)
        if kind=='xbar':
            result=chart_result(m,m-3*se,m+3*se,means if observed_subgroups else [],grand_mean=m,Rbar=r,standard_error=se,n=n)
        else:
            result=chart_result(r,r*FACTORS[n][2],r*FACTORS[n][3],ranges if observed_subgroups else [],Rbar=r,n=n)
        if len(means)>1:
            midpoint=len(means)//2
            result['first_half_mean']=float(means[:midpoint].mean())
            result['second_half_mean']=float(means[midpoint:].mean())
            result['first_half_mean_sd']=float(means[:midpoint].std(ddof=1)) if midpoint>1 else 0
            result['second_half_mean_sd']=float(means[midpoint:].std(ddof=1)) if len(means)-midpoint>1 else 0
        return result
    if kind=='range_identity':
        r=number(d['rbar'],'rbar',0); l=number(d['lcl'],'lcl',0,r)
        if l==0: raise ValueError('Clipped LCL=0 does not uniquely determine UCL')
        return dict(CL=r,LCL=l,UCL=2*r-l,values=[])
    if kind=='p':
        n=integer(d['n'],'n')
        values=np.array([])
        if 'counts' in d:
            counts=vector(d['counts'],'counts',0,n)
            if np.any(counts!=np.floor(counts)): raise ValueError('counts must be integers')
            values=counts/n
        elif 'proportions' in d: values=vector(d['proportions'],'proportions',0,1)
        if 'p' in d: p=number(d['p'],'p',0,1)
        elif len(values): p=float(values.mean())
        else: raise ValueError('Provide p, counts, or proportions')
        se=math.sqrt(p*(1-p)/n)
        return chart_result(p,max(0,p-3*se),min(1,p+3*se),values,n=n,standard_error=se,
            observed_proportion=float(values.mean()) if len(values) else None,
            center_source='specified target' if 'p' in d else 'estimated from equal-sized subgroups')
    if kind=='proportion_test':
        n=integer(d['n'],'n'); s=integer(d['successes'],'successes',0)
        if s>n: raise ValueError('successes cannot exceed n')
        p0=number(d['p0'],'p0',0,1); alpha=number(d.get('alpha',.05),'alpha',0,1)
        if not 0<p0<1 or not 0<alpha<1: raise ValueError('p0 and alpha must be strictly between 0 and 1')
        observed=s/n; z=(observed-p0)/math.sqrt(p0*(1-p0)/n)
        pvalue=float(stats.norm.sf(z))
        return dict(observed_proportion=observed,z=z,p_value=pvalue,
                    exact_binomial_p_value=float(stats.binomtest(s,n,p0,alternative='greater').pvalue),
                    alpha=alpha,reject_H0=pvalue<alpha)
    if kind=='pareto':
        counts=d['counts']
        if not isinstance(counts,dict) or not counts: raise ValueError('counts must be a nonempty mapping')
        vals={str(k):integer(v,'fault counts',0) for k,v in counts.items()}
        total=sum(vals.values())
        if total==0: raise ValueError('Pareto total must be positive')
        pairs=sorted([(k,v) for k,v in vals.items() if k!='Other'],key=lambda x:-x[1])
        if 'Other' in vals: pairs.append(('Other',vals['Other']))
        cumulative=np.cumsum([v for _,v in pairs])/total*100
        return dict(total=total,labels=[k for k,_ in pairs],counts=[v for _,v in pairs],
                    cumulative_percent=cumulative.tolist(),largest_category=pairs[0][0],largest_count=pairs[0][1])
    if kind=='acceptance':
        n=integer(d['n'],'n'); c=integer(d['c'],'c',0); N=integer(d['N'],'N')
        if c>n or n>N: raise ValueError('Require c <= n <= N')
        p=number(d['p'],'p',0,1); risk=d['risk']; model=d.get('model','binomial')
        if risk not in ('producer','consumer') or model not in ('binomial','poisson'): raise ValueError('Invalid risk or model')
        bin_accept=float(stats.binom.cdf(c,n,p)); pois_accept=float(stats.poisson.cdf(c,n*p))
        accept=pois_accept if model=='poisson' else bin_accept
        result=dict(probability=(1-accept if risk=='producer' else accept),
                    acceptance_probability=accept,binomial_probability=(1-bin_accept if risk=='producer' else bin_accept),
                    poisson_probability=(1-pois_accept if risk=='producer' else pois_accept),model=model)
        # A fixed finite lot must have an integer number of defectives. Never silently round N*p.
        D=N*p
        if abs(D-round(D))<1e-9:
            exact=float(stats.hypergeom.cdf(c,N,round(D),n))
            result['finite_lot_defectives']=round(D)
            result['finite_lot_probability']=1-exact if risk=='producer' else exact
        else: result['finite_lot_note']='N*p is noninteger; no exact fixed-lot result without specifying an integer D.'
        return result
    raise ValueError(f'Unsupported case kind: {kind}')
