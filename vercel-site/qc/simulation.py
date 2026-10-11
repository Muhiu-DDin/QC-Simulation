"""Seeded Monte Carlo experiments. Simulation validates a model, not real quality."""
import numpy as np
from scipy import stats
from .calculations import FACTORS

def probability_summary(events,theory):
    successes=int(np.count_nonzero(events)); trials=len(events); estimate=successes/trials
    # 99% Wilson interval is finite even when no events occur.
    z=float(stats.norm.ppf(.995)); denom=1+z*z/trials
    center=(estimate+z*z/(2*trials))/denom
    half=z*np.sqrt(estimate*(1-estimate)/trials+z*z/(4*trials*trials))/denom
    low=max(0,float(center-half)); high=min(1,float(center+half))
    return dict(estimate=estimate,theoretical_probability=float(theory),absolute_error=abs(estimate-theory),
                ci99_low=low,ci99_high=high,theory_in_ci99=low<=theory<=high,trials=trials,
                note='A valid 99% interval can miss the theoretical value by chance; many cases increase that chance.')

def simulate(case,result,trials,seed):
    rng=np.random.default_rng(seed); d=case['inputs']; kind=case['kind']
    if kind=='acceptance':
        n,c,p=int(d['n']),int(d['c']),d['p']; model=d.get('model','binomial')
        draws=rng.poisson(n*p,trials) if model=='poisson' else rng.binomial(n,p,trials)
        events=draws>c if d['risk']=='producer' else draws<=c
        output={'primary':probability_summary(events,result['probability'])}
        if 'finite_lot_defectives' in result:
            D=result['finite_lot_defectives']
            draw=rng.hypergeometric(D,int(d['N'])-D,n,trials)
            events=draw>c if d['risk']=='producer' else draw<=c
            output['finite_lot']=probability_summary(events,result['finite_lot_probability'])
        return output
    if kind=='proportion_test':
        draws=rng.binomial(int(d['n']),d['p0'],trials)
        return {'exact_null_tail':probability_summary(draws>=d['successes'],result['exact_binomial_p_value'])}
    if kind in ('xbar','range','p'):
        n=int(d['n']); cl=result['CL']; low=result['LCL']; high=result['UCL']
        if kind=='p':
            draws=rng.binomial(n,cl,trials)/n
            k=np.arange(n+1); pmf=stats.binom.pmf(k,n,cl)
            theory=float(pmf[(k/n<low)|(k/n>high)].sum())
            assumption='IID Bernoulli observations at the specified/estimated p; binomial tail is exact and discrete.'
        elif kind=='xbar':
            draws=rng.normal(cl,result['standard_error'],trials)
            theory=float(2*stats.norm.sf(3)) if result['standard_error']>0 else 0.
            assumption='Normal independent subgroup means with fixed fitted center and standard error; this is a model check, not a replay of observed data.'
        else:
            sigma=cl/FACTORS[n][0]
            # Generate in chunks so large trial counts do not allocate trials*n at once.
            pieces=[]
            for start in range(0,trials,10000):
                pieces.append(np.ptp(rng.normal(0,sigma,(min(10000,trials-start),n)),axis=1))
            draws=np.concatenate(pieces)
            mean=float(draws.mean()); mean_se=float(draws.std(ddof=1)/np.sqrt(trials))
            z=float(stats.norm.ppf(.995))
            return dict(simulated_mean=float(draws.mean()),target_mean=cl,
                        mean_standard_error=mean_se,mean_ci99_low=mean-z*mean_se,
                        mean_ci99_high=mean+z*mean_se,target_in_mean_ci99=mean-z*mean_se<=cl<=mean+z*mean_se,
                        mean_absolute_error=abs(float(draws.mean())-cl),
                        out_of_limits_fraction=float(np.mean((draws<low)|(draws>high))),trials=trials,
                        assumption='IID normal individual observations. R limits use rounded appendix factors; the range distribution is not normal.')
        return dict(out_of_limits=probability_summary((draws<low)|(draws>high),theory),
                    simulated_mean=float(draws.mean()),target_mean=cl,trials=trials,assumption=assumption)
    return {'note':'Deterministic arithmetic or Pareto counts: Monte Carlo is not applicable.'}
