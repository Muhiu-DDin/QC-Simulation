"""Portable plots plus an HTML portfolio report (no web server required)."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from .report_ui import render_report

plt.rcParams.update({'figure.dpi':140,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})

def plot_case(case,result,directory):
    kind=case['kind']; d=case['inputs']; filename=case['id']+'.png'
    if kind in ('xbar','range','p','range_identity'):
        fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
        values=np.array(result['values']); x=np.arange(1,len(values)+1)
        if len(values):
            ax.plot(x,values,'o-',color='#2563a6',markersize=4,lw=1)
            mask=(values<result['LCL'])|(values>result['UCL'])
            ax.scatter(x[mask],values[mask],color='#c23b32',zorder=4,label='Outside limits')
            labels=d.get('labels')
            if labels: ax.set_xticks(x,labels,rotation=45)
        else: ax.set_xlim(0,2); ax.set_xticks([])
        for key,color,style in [('CL','#28784b','-'),('LCL','#c23b32','--'),('UCL','#c23b32','--')]:
            ax.axhline(result[key],color=color,ls=style,label=f'{key} = {result[key]:.6g}')
        ax.set_xlabel('Subgroup / time order'); ax.set_ylabel('Proportion' if kind=='p' else d.get('unit','Value'))
        ax.legend(loc='best',fontsize=8); ax.grid(alpha=.18)
    elif kind=='pareto':
        fig,ax=plt.subplots(figsize=(11,6),layout='constrained')
        x=np.arange(len(result['labels'])); ax.bar(x,result['counts'],color='#2563a6')
        ax.set_xticks(x,result['labels'],rotation=50,ha='right',fontsize=8)
        ax.set_ylabel('Number of faults / complaints')
        second=ax.twinx(); second.plot(x,result['cumulative_percent'],'o-',color='#c23b32',markersize=4)
        second.set_ylim(0,105); second.set_ylabel('Cumulative percent'); second.axhline(80,ls=':',color='gray')
        for i,count in enumerate(result['counts']): ax.text(i,count,str(count),ha='center',va='bottom',fontsize=8)
    elif kind=='acceptance':
        fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
        p=np.linspace(0,.05,401); n,c=d['n'],d['c']
        ax.plot(p*100,stats.binom.cdf(c,n,p),label='Binomial')
        ax.plot(p*100,stats.poisson.cdf(c,n*p),'--',label='Poisson approximation')
        N=d['N']; D=np.arange(int(N*.05)+1)
        ax.plot(D/N*100,stats.hypergeom.cdf(c,N,D,n),':',label='Fixed-lot hypergeometric')
        ax.scatter([d['p']*100],[result['acceptance_probability']],color='#c23b32',zorder=4,label='Requested input')
        ax.set_xlabel('Incoming defective percent'); ax.set_ylabel('Probability of accepting lot')
        ax.set_ylim(0,1.03); ax.legend(fontsize=8); ax.grid(alpha=.18)
    elif kind=='proportion_test':
        fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
        z=result['z']; x=np.linspace(min(-4,z-1),max(4,z+1),800)
        ax.plot(x,stats.norm.pdf(x),color='#2563a6'); ax.fill_between(x,stats.norm.pdf(x),where=x>=z,color='#c23b32',alpha=.3)
        ax.axvline(z,color='#c23b32',label=f'Observed z = {z:.4f}')
        ax.set_xlabel('Standard normal test statistic'); ax.set_ylabel('Density'); ax.legend()
    else: return None
    ax.set_title(case['id']+' | '+case['title'])
    path=directory/filename; fig.savefig(path); plt.close(fig)
    return 'graphs/'+filename

def write_report(records,out,metadata,reuse_graphs=False):
    out=Path(out); graphdir=out/'graphs'; graphdir.mkdir(parents=True,exist_ok=True)
    summaries=[]; plots={}
    for rec in records:
        c=rec['case']; r=rec['calculated']
        plot='graphs/'+c['id']+'.png' if reuse_graphs and graphdir.joinpath(c['id']+'.png').is_file() else plot_case(c,r,graphdir)
        plots[c['id']]=plot
        comparisons=rec['comparisons']
        for name,comparison in comparisons.items():
            for field in comparison['fields']:
                summaries.append(dict(case=c['id'],reference=name,provenance=comparison.get('provenance',''),
                    status=comparison['status'],**field))
    book_matches=sum(r['comparisons']['book']['status']=='MATCH' for r in records)
    book_mismatches=sum(r['comparisons']['book']['status']=='MISMATCH' for r in records)
    book_errata=sum(r['comparisons']['book']['status']=='SOURCE_ERRATUM' for r in records)
    independent_mismatches=sum(r['comparisons']['independent']['status']=='MISMATCH' for r in records)
    document=render_report(records,metadata,plots)
    out.joinpath('report.html').write_text(document,encoding='utf-8')
    out.joinpath('results.json').write_text(json.dumps(dict(metadata=metadata,records=records),indent=2,allow_nan=False),encoding='utf-8')
    fields=['case','reference','provenance','status','field','expected','actual','absolute_error','tolerance','passed']
    with out.joinpath('comparison.csv').open('w',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=fields); writer.writeheader(); writer.writerows(summaries)
    return dict(cases=len(records),book_matches=book_matches,book_mismatches=book_mismatches,book_errata=book_errata,
                independent_mismatches=independent_mismatches,report=str(out/'report.html'))
