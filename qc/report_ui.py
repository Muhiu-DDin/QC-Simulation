"""Presentation layer. Statistical values and machine-readable exports stay intact."""
import html
import math

def esc(value): return html.escape(str(value),quote=True)

def display(value):
    if value is None: return '—'
    if isinstance(value,bool): return 'Yes' if value else 'No'
    if isinstance(value,(int,float)):
        if not math.isfinite(value): return '—'
        if value==0: return '0'
        if abs(value)<.000001: return f'{value:.3g}'
        return f'{value:,.6f}'.rstrip('0').rstrip('.')
    if isinstance(value,list):
        return '; '.join(', '.join(display(x) for x in row) if isinstance(row,list) else display(row) for row in value)
    if isinstance(value,dict): return '; '.join(f'{k}: {display(v)}' for k,v in value.items())
    return str(value)

LABELS={'CL':'Center line','LCL':'Lower control limit','UCL':'Upper control limit',
    'n':'Subgroup size','N':'Lot size','mean':'Grand mean','rbar':'Average range','p':'Target proportion',
    'p0':'Null proportion','se':'Standard error','c':'Acceptance number','counts':'Observed counts',
    'observations':'Measurements by subgroup','means':'Subgroup means','ranges':'Subgroup ranges',
    'proportions':'Observed proportions','probability':'Risk probability','p_value':'P-value',
    'z':'Z statistic','total':'Total count','largest_count':'Largest category count','largest_category':'Largest category',
    'observed_proportion':'Observed proportion','successes':'Observed events','risk':'Risk type',
    'model':'Probability model','alpha':'Significance level','unit':'Measurement unit','attribute':'Measured attribute'}
KINDS={'xbar':'Mean control chart','range':'Range control chart','p':'Proportion control chart',
    'range_identity':'Range control limits','acceptance':'Acceptance sampling',
    'pareto':'Pareto analysis','proportion_test':'Proportion hypothesis test'}

def badge(status):
    wording,tone={'MATCH':('Verified','good'),'MISMATCH':('Review required','bad'),
        'SOURCE_ERRATUM':('Textbook correction','warn'),'NO_BOOK_ANSWER':('No reference available','neutral')}.get(status,('Not compared','neutral'))
    return f'<span class="badge {tone}"><span class="dot"></span>{wording}</span>'

def comparison_panel(name,comparison):
    source=comparison.get('provenance','')
    if name=='book':
        title='Graph comparison' if source=='approximate_graph_reading' else 'Textbook comparison'
        subtitle='Compared with the approximate reading of the textbook graph.' if source=='approximate_graph_reading' else 'Compared with the published textbook answer.'
    else:
        title='Independent validation'; subtitle='Compared with a separately calculated reference answer.'
    if not comparison['fields']:
        return f'<div class="empty-reference"><span>{esc(title)}</span><p>No stored answer is available for these inputs.</p></div>'
    rows=[]
    for f in comparison['fields']:
        field=LABELS.get(f['field'],f['field'].replace('_',' ').capitalize())
        outcome='<span class="check good-text">✓ Verified</span>' if f['passed'] else '<span class="check bad-text">Review</span>'
        rows.append(f'<tr><th scope="row">{esc(field)}</th><td>{esc(display(f["expected"]))}</td><td class="calculated">{esc(display(f["actual"]))}</td><td>{esc(display(f["absolute_error"]))}</td><td>{esc(display(f["tolerance"]))}</td><td>{outcome}</td></tr>')
    note=f'<p class="reference-note">{esc(comparison["note"])}</p>' if comparison.get('note') else ''
    return f'''<div class="comparison"><div class="panel-heading"><div><h3>{title}</h3><p>{subtitle}</p></div>{badge(comparison['status'])}</div>
<div class="table-scroll"><table><thead><tr><th>Measure</th><th>Reference answer</th><th>Calculated answer</th><th>Difference</th><th>Allowed difference</th><th>Result</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>{note}</div>'''

def simulation_panel(simulation):
    content=[]
    for name,value in simulation.items():
        if isinstance(value,dict) and 'estimate' in value:
            title={'primary':'Sampling probability','finite_lot':'Sampling without replacement',
                'exact_null_tail':'Exact hypothesis-test probability','out_of_limits':'Probability outside control limits'}.get(name,name.replace('_',' ').capitalize())
            content.append(f'''<div class="simulation-block"><h4>{esc(title)}</h4><div class="simulation-grid">
<div><span>Theoretical probability</span><strong>{esc(display(value['theoretical_probability']))}</strong></div>
<div><span>Simulated probability</span><strong>{esc(display(value['estimate']))}</strong></div>
<div><span>99% confidence interval</span><strong>{esc(display(value['ci99_low']))} – {esc(display(value['ci99_high']))}</strong></div>
</div>{'<p class="reference-note">The theoretical value falls outside this interval. A simulation interval can miss it by chance.</p>' if not value['theory_in_ci99'] else ''}</div>''')
    if 'simulated_mean' in simulation:
        content.append(f'<p class="simulation-mean">Simulated mean <strong>{esc(display(simulation["simulated_mean"]))}</strong><span>Reference mean <strong>{esc(display(simulation["target_mean"]))}</strong></span></p>')
        if 'mean_ci99_low' in simulation:
            content.append(f'<p class="muted">99% confidence interval for the mean: {esc(display(simulation["mean_ci99_low"]))} – {esc(display(simulation["mean_ci99_high"]))}.</p>')
    if simulation.get('assumption'): content.append(f'<p class="muted">{esc(simulation["assumption"])}</p>')
    if not content: content.append('<p class="muted">This exercise uses direct arithmetic; a random simulation is not required.</p>')
    count=f'<span class="detail-meta">{simulation["trials"]:,} trials</span>' if simulation.get('trials') else ''
    return f'<details class="detail-panel"><summary>Simulation verification{count}</summary><div class="detail-body">{"".join(content)}</div></details>'

def render_report(records,metadata,plots):
    sections=[]
    for index,record in enumerate(records):
        case=record['case']; result=record['calculated']; id=case['id']
        cards=[]
        fields=['CL','LCL','UCL'] if 'CL' in result else (['probability','acceptance_probability'] if 'probability' in result else (['observed_proportion','z','p_value'] if 'p_value' in result else ['total','largest_category','largest_count']))
        for field in fields:
            if field in result: cards.append(f'<div class="metric"><span>{esc(LABELS.get(field,field.replace("_"," ").capitalize()))}</span><strong>{esc(display(result[field]))}</strong></div>')
        inputs=''.join(f'<tr><th scope="row">{esc(LABELS.get(k,k.replace("_"," ").capitalize()))}</th><td>{esc(display(v))}</td></tr>' for k,v in case['inputs'].items())
        source=f'Textbook page {case["page"]} <span>· PDF page {case["pdf_page"]}</span>' if 'page' in case else 'Custom input'
        plot=plots.get(id)
        chart=f'<div class="chart-panel"><div class="chart-heading"><h3>{"Operating characteristic curve" if case["kind"]=="acceptance" else "Pareto chart" if case["kind"]=="pareto" else "Test distribution" if case["kind"]=="proportion_test" else "Control chart"}</h3><a href="{esc(plot)}" download>Download chart ↗</a></div><img src="{esc(plot)}" alt="{esc(id)} statistical chart" loading="{"eager" if index==0 else "lazy"}"></div>' if plot else ''
        interpretation=f'<div class="interpretation"><h3>Interpretation</h3><p>{esc(case["interpretation"])}</p></div>' if case.get('interpretation') else ''
        comparisons=''.join(comparison_panel(name,comp) for name,comp in record['comparisons'].items())
        sections.append(f'''<section class="exercise" id="{esc(id)}" data-search="{esc((id+' '+case['title']).lower())}">
<div class="exercise-heading"><div><span class="eyebrow">{esc(KINDS.get(case['kind'],case['kind']))}</span><h2><span class="exercise-id">{esc(id)}</span>{esc(case['title'])}</h2><p class="source">{source}</p></div><a class="subtle-link" href="#top">Back to top ↑</a></div>
<div class="metrics">{''.join(cards)}</div>{comparisons}{chart}{interpretation}
<details class="detail-panel"><summary>Input values<span class="detail-meta">{len(case['inputs'])} parameters</span></summary><div class="detail-body table-scroll"><table class="input-table"><tbody>{inputs}</tbody></table></div></details>
{simulation_panel(record['simulation'])}</section>''')
    attention=sum(any(c['status'] in ('MISMATCH','SOURCE_ERRATUM') for c in r['comparisons'].values()) for r in records)
    verified=sum(any(c['status']=='MATCH' for c in r['comparisons'].values()) and not any(c['status'] in ('MISMATCH','SOURCE_ERRATUM') for c in r['comparisons'].values()) for r in records)
    navigation=''.join(f'<a href="#{esc(r["case"]["id"])}" data-search="{esc((r["case"]["id"]+" "+r["case"]["title"]).lower())}"><span>{esc(r["case"]["id"])}</span><small>{esc(r["case"]["title"])}</small></a>' for r in records)
    sidebar=f'<aside><p class="index-heading">Exercises <span>{len(records)}</span></p><label class="sr-only" for="search">Find an exercise</label><input id="search" type="search" placeholder="Search by question or topic"><nav class="exercise-nav" aria-label="Exercise index">{navigation}</nav><p id="empty-search" hidden>No matching exercises.</p></aside>' if len(records)>1 else ''
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quality Control | Results</title><style>'''+CSS+'''</style></head><body>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="#top">Quality Control<span class="chapter-label">Chapter 10</span></a><nav class="report-nav" aria-label="Report navigation"><a href="#top" aria-current="location">Overview</a><a href="#exercises">Exercises</a><a href="https://vercel-site-tawny-omega.vercel.app/calculator.html">Calculator</a><a href="#downloads">Downloads</a></nav><span class="course">Software Testing · Part 2B</span></div></header>
<main id="top"><header class="report-heading"><div><p class="eyebrow">Statistical analysis</p><h1>Quality control results</h1><p class="lede">Calculated answers, reference comparisons and process charts.</p></div><a class="download-button" href="comparison.csv" download>Export comparisons ↓</a></header>
<div class="overview"><div><span>Exercises analysed</span><strong>'''+str(len(records))+'''</strong></div><div><span>Results verified</span><strong class="good-text">'''+str(verified)+'''</strong></div><div><span>Items to review</span><strong>'''+str(attention)+'''</strong></div></div>
<div id="exercises" class="workspace '''+('with-index' if sidebar else '')+'''">'''+sidebar+'''<div class="results">'''+''.join(sections)+'''</div></div>
<footer id="downloads"><span>Chapter 10 · Quality and Quality Control</span><div class="download-links"><a href="comparison.csv" download>Comparison spreadsheet</a><a href="results.json" download>Full results (JSON)</a></div></footer></main>
<script>const search=document.getElementById('search');if(search){search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();let count=0;document.querySelectorAll('.exercise-nav a').forEach(a=>{a.hidden=!a.dataset.search.includes(q);if(!a.hidden)count++});document.querySelectorAll('.exercise').forEach(s=>{s.hidden=!s.dataset.search.includes(q)});document.getElementById('empty-search').hidden=count!==0;});}
const reportLinks=document.querySelectorAll('.report-nav a[href^="#"]');function updateNavigation(){const hash=location.hash||'#top';reportLinks.forEach(a=>{const active=a.getAttribute('href')===hash||(a.getAttribute('href')==='#exercises'&&!['#top','#downloads'].includes(hash));if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}window.addEventListener('hashchange',updateNavigation);updateNavigation();
document.querySelectorAll('.exercise-nav a').forEach(a=>a.addEventListener('click',()=>{document.querySelectorAll('.exercise-nav a').forEach(link=>link.removeAttribute('aria-current'));a.setAttribute('aria-current','location');}));
</script></body></html>'''

CSS='''
:root{--ink:#192d40;--muted:#647586;--line:#e5eaee;--teal:#087f74;--bg:#f4f6f8}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:90px}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 "Segoe UI",Arial,sans-serif}a{color:var(--teal);text-decoration:none}a:hover{text-decoration:underline}button,input{font:inherit}[hidden]{display:none!important}.topbar{height:74px;background:#fff;border-bottom:1px solid var(--line)}.topbar-inner{max-width:1360px;margin:auto;padding:0 40px;height:100%;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;align-items:center;gap:12px;color:var(--ink);font-weight:650;font-size:17px}.brand:hover{text-decoration:none}.brand-mark{background:#12384a;color:#fff;display:grid;place-items:center;border-radius:10px;width:40px;height:40px;font-size:13px;letter-spacing:1px}.brand small{display:block;font-size:11px;font-weight:450;color:var(--muted);margin-top:-2px}.course{font-size:12px;color:var(--muted)}.course span{margin:0 9px;color:#bdc7cf}main{max-width:1360px;margin:auto;padding:38px 40px 20px}.report-heading{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:28px}.eyebrow{display:block;text-transform:uppercase;letter-spacing:1.6px;font-size:10px;font-weight:700;color:var(--teal);margin:0 0 9px}h1{font-size:34px;letter-spacing:-1.2px;line-height:1.2;margin:0 0 10px;font-weight:650}.lede{margin:0;color:var(--muted);font-size:14px}.download-button{display:inline-flex;white-space:nowrap;align-items:center;padding:10px 17px;background:white;border:1px solid #d4dfe5;border-radius:7px;color:var(--ink);font-size:12px;font-weight:600}.download-button:hover{background:#eaf3f2;text-decoration:none}.overview{display:grid;grid-template-columns:repeat(3,1fr);background:#fff;border:1px solid var(--line);border-radius:10px;margin-bottom:28px;padding:18px 0}.overview>div{padding:0 26px;border-right:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:14px}.overview>div:last-child{border:0}.overview span{color:var(--muted);font-size:12px}.overview strong{font-size:24px;font-weight:650;font-variant-numeric:tabular-nums}.workspace{display:grid;gap:24px}.with-index{grid-template-columns:205px minmax(0,1fr)}aside{position:sticky;top:24px;align-self:start}aside .eyebrow{color:var(--muted)}aside input{width:100%;border:1px solid #d8e1e7;border-radius:7px;padding:9px 11px;background:#fff;outline:none;font-size:12px;margin-bottom:12px}aside input:focus{border-color:var(--teal);box-shadow:0 0 0 3px #087f7414}nav{max-height:70vh;overflow:auto;padding-right:6px}nav a{display:block;padding:9px 10px;border-radius:6px;margin-bottom:3px;color:var(--ink)}nav a:hover{background:#e5eeef;text-decoration:none}nav a span{font-size:12px;font-weight:650;display:block}nav small{font-size:11px;color:var(--muted);display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.results{min-width:0}.exercise{background:white;border:1px solid var(--line);border-radius:12px;padding:28px;margin-bottom:24px;box-shadow:0 2px 5px #142e4503}.exercise-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:23px}h2{font-size:23px;font-weight:650;letter-spacing:-.5px;line-height:1.35;margin:0}.exercise-id{font-size:13px;font-weight:600;letter-spacing:0;display:inline-block;border:1px solid #dce5e9;background:#f5f8f9;padding:3px 8px;border-radius:5px;margin-right:12px;vertical-align:middle;color:#405767}.source{font-size:11px;color:var(--muted);margin:8px 0 0}.source span{color:#8996a2}.subtle-link{font-size:11px;color:#7c8b96;white-space:nowrap;padding-top:4px}.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:28px}.metric{padding:17px 18px;background:#f7fafb;border:1px solid #e7eef0;border-radius:8px}.metric:first-child{border-top:3px solid var(--teal);padding-top:15px}.metric span{display:block;font-size:11px;color:var(--muted);margin-bottom:5px}.metric strong{display:block;font-size:25px;font-weight:600;letter-spacing:-.6px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.comparison{border:1px solid var(--line);border-radius:8px;margin-bottom:16px;overflow:hidden}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:17px 19px}h3{font-size:14px;font-weight:650;margin:0}.panel-heading p{font-size:11px;color:var(--muted);margin:3px 0 0}.badge{display:inline-flex;align-items:center;gap:6px;border-radius:20px;padding:4px 10px;font-size:10px;font-weight:650;white-space:nowrap}.dot{width:5px;height:5px;border-radius:50%;background:currentColor}.good{background:#e7f5ef;color:#16704f}.bad{background:#fcecea;color:#a7352a}.warn{background:#fff3d9;color:#966817}.neutral{background:#edf1f4;color:#647586}.good-text{color:#16704f}.bad-text{color:#a7352a}.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;text-align:left;font-size:12px;font-variant-numeric:tabular-nums}thead{background:#f6f8fa;color:#667889;border-top:1px solid var(--line)}thead th{font-size:10px;font-weight:600;white-space:nowrap;padding:11px 16px}tbody td,tbody th{padding:12px 16px;border-top:1px solid #edf0f3;white-space:nowrap}tbody th{font-weight:500;color:#344e61}.calculated{color:#144a5b;font-weight:650}.check{font-size:10px;font-weight:600}.reference-note{margin:0;padding:12px 19px;background:#fffaf0;color:#84622e;font-size:11px;border-top:1px solid #f1e9d8}.empty-reference{border:1px dashed #dce4e8;border-radius:8px;padding:13px 18px;margin-bottom:14px}.empty-reference span{font-size:12px;font-weight:600}.empty-reference p{margin:3px 0 0;color:var(--muted);font-size:12px}.chart-panel{margin:27px 0 22px}.chart-heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.chart-heading a{font-size:11px}img{display:block;max-width:100%;height:auto}.interpretation{background:#f3f8f8;border-left:3px solid #80b7af;border-radius:0 6px 6px 0;padding:15px 18px;margin:18px 0}.interpretation p{font-size:12px;color:#486270;margin:6px 0 0}.detail-panel{border-top:1px solid var(--line)}summary{list-style:none;cursor:pointer;padding:16px 2px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:10px}summary::-webkit-details-marker{display:none}summary:before{content:'+';font-size:15px;color:var(--teal);font-weight:400}details[open] summary:before{content:'−'}.detail-meta{margin-left:auto;color:var(--muted);font-size:10px;font-weight:400}.detail-body{padding:0 0 18px}.input-table th{width:190px;white-space:normal}.input-table td{white-space:normal;overflow-wrap:anywhere;color:#4a6172}.input-table tr:first-child>*{border-top:0}.simulation-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;background:#f7fafb;padding:14px;border-radius:6px}.simulation-grid span{display:block;font-size:10px;color:var(--muted)}.simulation-grid strong{display:block;font-size:15px;font-weight:600;margin-top:4px}.simulation-block{margin:0 0 15px}h4{font-size:12px;margin:0 0 10px;font-weight:600}.simulation-mean{font-size:12px;color:var(--muted)}.simulation-mean strong{color:var(--ink);margin-left:6px}.simulation-mean span{margin-left:24px}.muted{font-size:11px;color:var(--muted)}footer{display:flex;justify-content:space-between;gap:16px;font-size:11px;color:#8695a0;padding:4px 0 20px}.sr-only{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip:rect(0,0,0,0)}
@media(min-width:1100px){.workspace:not(.with-index) .exercise{padding:30px 34px}.workspace:not(.with-index) .metric strong{font-size:29px}}
@media(max-width:850px){.topbar-inner{padding:0 20px}main{padding:25px 18px}.with-index{grid-template-columns:1fr}aside{position:static}nav{display:flex;gap:5px;max-height:110px;flex-wrap:wrap}nav a{background:white;border:1px solid var(--line);max-width:150px}.course{display:none}.exercise{padding:20px}.report-heading{align-items:flex-start}h1{font-size:28px}.overview>div{padding:0 14px;display:block}.overview strong{display:block}.panel-heading{padding:14px}.source span{display:none}.subtle-link{display:none}}
@media(max-width:520px){.report-heading{display:block}.download-button{margin-top:17px}.overview{margin-bottom:20px}.overview span{font-size:10px}.metrics{gap:8px;grid-template-columns:repeat(3,minmax(0,1fr))}.metric{padding:12px 9px}.metric:first-child{padding-top:10px}.metric strong{font-size:18px}.metric span{font-size:9px}h2{font-size:20px}.exercise-id{display:block;width:max-content;margin-bottom:8px}.panel-heading{align-items:flex-start}.panel-heading p{max-width:180px}.simulation-grid{grid-template-columns:1fr}.simulation-mean span{display:block;margin:8px 0 0}footer{display:block}footer a{display:block;margin-top:5px}}
@media print{body{background:white}.topbar,aside,.download-button,.subtle-link,.chart-heading a,footer a{display:none}.with-index{grid-template-columns:1fr}main{padding:0;max-width:none}.exercise{box-shadow:none;break-inside:avoid}.overview{margin-bottom:15px}details:not([open]){display:none}h1{font-size:25px}img{max-height:330px;object-fit:contain}}

/* Report navigation: plain typography, thin rules and visible current section. */
.topbar{height:64px;position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid #dbe2e7}
.topbar-inner{gap:36px}.brand{font-size:16px;letter-spacing:-.3px;font-weight:600;gap:14px;white-space:nowrap}
.chapter-label{border-left:1px solid #d9e0e5;padding-left:14px;color:#6c7b88;font-size:12px;font-weight:400;letter-spacing:0}
.report-nav{align-self:stretch;display:flex;gap:26px;margin:0 auto 0 12px;overflow:visible;padding:0;max-height:none}
.report-nav a{display:flex;align-items:center;padding:0 2px;margin:0;border-radius:0;border-bottom:2px solid transparent;color:#657481;font-size:12px;font-weight:500}
.report-nav a:hover{background:none;color:#192d40;text-decoration:none;border-bottom-color:#c4ced6}
.report-nav a[aria-current]{color:#192d40;border-bottom-color:#192d40;font-weight:600}
.course{white-space:nowrap;font-size:11px;color:#7a8791}aside{top:90px}
.index-heading{font-size:12px;font-weight:600;color:#344e61;margin:0 0 14px;display:flex;justify-content:space-between;align-items:center}
.index-heading span{font-size:11px;color:#84929d;font-weight:400}aside input{border-radius:4px;margin-bottom:16px;padding:9px 10px;font-size:11px}
.exercise-nav{border-left:1px solid #dce3e8;max-height:calc(100vh - 200px);padding:0 5px 0 0}
.exercise-nav a{border-left:2px solid transparent;margin:0 0 1px -1px;border-radius:0;padding:9px 12px}
.exercise-nav a:hover{background:#edf1f3;border-left-color:#adbcc6}
.exercise-nav a[aria-current]{background:#e9eef1;border-left-color:#23495b}
.exercise-nav a span{font-size:11px;font-weight:600}.exercise-nav small{font-size:10px;margin-top:2px}
.download-links{display:flex;gap:24px}.download-links a{font-size:11px}
a:focus-visible{outline:2px solid #087f74;outline-offset:4px}
@media(max-width:850px){.topbar-inner{gap:20px}.course{display:none}.report-nav{gap:20px;margin-left:auto;margin-right:0}.with-index aside{position:static}.exercise-nav{display:block;border-left:1px solid #dce3e8;max-height:190px}.exercise-nav a{background:transparent;border:0;border-left:2px solid transparent;max-width:none}.exercise-nav a span,.exercise-nav small{display:inline}.exercise-nav small{margin-left:12px}.chapter-label{font-size:11px}.download-links{gap:16px}}
@media(max-width:520px){.topbar{height:auto}.topbar-inner{padding:12px 18px 0;flex-wrap:wrap;gap:10px}.brand{font-size:14px}.report-nav{width:100%;margin:0;gap:24px;height:38px}.report-nav a{font-size:11px}.download-links{display:block}.download-links a{display:block;margin-top:8px}html{scroll-padding-top:110px}}
/* Navy structure, muted teal accents, and quiet tinted surfaces. */
:root{--ink:#183247;--muted:#5c7283;--line:#dce6ec;--teal:#146f73;--bg:#edf2f5}
.topbar{background:#153449;border-bottom-color:#244a60;box-shadow:0 2px 8px #16344912}
.brand{color:#f6fafc}.brand:hover{color:#fff}.chapter-label{border-left-color:#476276;color:#bcced9}
.report-nav a{color:#c2d2de}.report-nav a:hover{color:#fff;border-bottom-color:#8cb3c1}
.report-nav a[aria-current]{color:#fff;border-bottom-color:#67b7b2}.course{color:#b5c9d6}
.report-heading{border-left:3px solid #247e82;padding-left:18px}.report-heading .eyebrow{color:#146f73}
h1{color:#17384f}.download-button{background:#1c5269;color:#fff;border-color:#1c5269;box-shadow:0 2px 4px #1c526912}
.download-button:hover{background:#163e52;color:#fff;border-color:#163e52}
.overview{border-top:3px solid #284f68;box-shadow:0 3px 12px #1b3d5105}
.overview>div:first-child strong{color:#234f6b}.overview>div:nth-child(2) strong{color:#17745c}
.overview>div:nth-child(3) strong{color:#536779}
.exercise{border-color:#dce6ec;box-shadow:0 4px 16px #17384f05}
.exercise-id{background:#eaf1f6;border-color:#cddde7;color:#28516c}
.metric{background:#f1f6f9;border-color:#dce7ee}.metric strong{color:#234c67}
.metric:first-child{background:#ecf6f4;border-color:#d2e6e1;border-top-color:#1d807a}
.metric:first-child strong{color:#17665f}.metric:nth-child(2){border-top:3px solid #63819c;padding-top:15px}
.metric:nth-child(3){border-top:3px solid #305d79;padding-top:15px}
.panel-heading{background:#f0f5f8;border-bottom:1px solid #e0e9ef}.panel-heading h3{color:#254d66}
thead{background:#e8f0f5;color:#486579;border-top:0}.calculated{color:#126569}
tbody tr:nth-child(even){background:#fafcfd}.good{background:#dfefe7;color:#176448}
.interpretation{background:#eaf3f3;border-left-color:#3f9290}.simulation-grid{background:#eef4f8}
.chart-heading{border-bottom:1px solid #e2eaf0;padding-bottom:12px}.chart-heading h3{color:#28546d}
.exercise-nav a:hover{background:#e2edf2;border-left-color:#759bac}
.exercise-nav a[aria-current]{background:#dcebee;border-left-color:#18777b}.exercise-nav a[aria-current] span{color:#126569}
aside input{border-color:#ccdce5}.detail-panel summary:hover{color:#146f73;background:#f8fbfc}
footer{border-top:1px solid #d6e1e8;padding-top:18px}.download-links a{color:#285d76}
@media(max-width:520px){.metric:nth-child(2),.metric:nth-child(3){padding-top:10px}.report-heading{padding-left:14px}}
/* Reference palette: charcoal, deep red, and white. */
:root{--ink:#f4f4f5;--muted:#bdc0c8;--line:#50525c;--teal:#ed858c;--bg:#292a32}
body{background:#292a32;color:#f4f4f5}
.topbar{background:#23242b;border-bottom:3px solid #be303a;box-shadow:none}
.brand,.brand:hover{color:#fff}.chapter-label{color:#c6c7ce;border-left-color:#62636d}
.report-nav a{color:#c9cbd2}.report-nav a:hover{color:#fff;border-bottom-color:#df727a}
.report-nav a[aria-current]{color:#fff;border-bottom-color:#d94852}.course{color:#bfc1c9}
.report-heading{border-left:4px solid #c3333e}.report-heading .eyebrow{color:#ef949b}
h1{color:#fff}.lede{color:#c3c5ce}a{color:#efa0a6}
.download-button{background:#be303a;color:#fff;border-color:#d24a53;box-shadow:none}
.download-button:hover{background:#a52832;border-color:#ca424d;color:#fff}
.overview{background:#31323c;border-color:#51535e;border-top:3px solid #be303a;box-shadow:none}
.overview span{color:#c8cad2}.overview>div:first-child strong,.overview>div:nth-child(2) strong{color:#fff}
.overview>div:nth-child(3) strong{color:#e2b6b9}
.exercise{background:#2e2f38;border-color:#50525c;box-shadow:none}
.exercise-heading .eyebrow{color:#ef949b}h2{color:#fff}.exercise-id{background:#423038;border-color:#87515a;color:#ffe1e4}
.source{color:#c4c5ce}.source span{color:#a6a8b3}.subtle-link{color:#cacbd2}
.metric,.metric:first-child{background:#353640;border-color:#50525c;border-top-color:#be303a}
.metric:nth-child(2),.metric:nth-child(3){border-top-color:#be303a}
.metric span{color:#d0d1d8}.metric strong,.metric:first-child strong{color:#fff}
.comparison{border-color:#646670}.panel-heading{background:#be303a;border-bottom-color:#d07078}
.panel-heading h3{color:#fff}.panel-heading p{color:#ffe5e7}
thead{background:#393a45;color:#eeeef1}tbody th{color:#f0f0f3}
tbody td,tbody th{border-top-color:#52545f}tbody tr:nth-child(even){background:#32333d}
.calculated{color:#fff}.check.good-text,.good-text{color:#bfe2ce}
.good{background:#263f37;color:#d1efdf}.bad{background:#582b33;color:#ffd7dc}
.warn{background:#54432b;color:#ffe0aa}.neutral{background:#444550;color:#ededf2}
.panel-heading .good{background:#fff;color:#3d6655}.panel-heading .bad{background:#fff;color:#a52e38}
.panel-heading .warn{background:#fff1d9;color:#79591f}
.reference-note{background:#40352e;border-top-color:#635344;color:#f0d6b6}
.empty-reference{border-color:#646670;background:#32333c}.empty-reference p{color:#c6c8d0}
.chart-heading{border-bottom-color:#555761}.chart-heading h3{color:#f5f5f7}
.chart-panel img{background:#fff;border:1px solid #6a6c76;border-radius:4px}
.interpretation{background:#3a3037;border-left-color:#be303a}.interpretation h3{color:#fff}
.interpretation p{color:#e3d4d8}.detail-panel{border-top-color:#50525c}
.detail-panel summary:hover{color:#fff;background:#383943}summary:before{color:#efa0a6}
.detail-meta,.muted{color:#c0c2cc}.input-table td{color:#e0e1e6}
.simulation-grid{background:#393a44}.simulation-grid span{color:#c5c7d0}.simulation-grid strong{color:#fff}
.simulation-mean{color:#c5c7d0}.simulation-mean strong{color:#fff}
.index-heading{color:#fff}.index-heading span{color:#bec0ca}
aside input{background:#34353e;border-color:#60626d;color:#fff}aside input::placeholder{color:#bcbec8}
aside input:focus{border-color:#e07880;box-shadow:0 0 0 3px #be303a25}
.exercise-nav{border-left-color:#61636f}.exercise-nav a{color:#f3f3f6}
.exercise-nav small{color:#bfc1cc}.exercise-nav a:hover{background:#3a343c;border-left-color:#df737c}
.exercise-nav a[aria-current]{background:#44313a;border-left-color:#d34651}
.exercise-nav a[aria-current] span{color:#ffd9de}
footer{border-top:3px solid #be303a;color:#c9cbd2}.download-links a{color:#f4b0b6}
a:focus-visible{outline-color:#f0929a}
@media print{.topbar,.download-button{display:none}:root{--ink:#192d40;--muted:#647586;--line:#dce3e8;--teal:#a52e38;--bg:#fff}body{background:#fff;color:#192d40}.report-heading{border-left:0;padding-left:0}h1,h2,h3,.metric strong,.metric:first-child strong,.chart-heading h3{color:#192d40}.overview,.exercise,.metric,.metric:first-child{background:#fff;color:#192d40;box-shadow:none}.overview span,.metric span,.source,.lede{color:#526579}.overview>div strong{color:#192d40!important}.comparison{border-color:#dce3e8}.panel-heading{background:#be303a}thead{background:#f0f1f3;color:#344e61}tbody th,.calculated{color:#192d40}tbody tr:nth-child(even){background:#f7f8fa}tbody td,tbody th{border-color:#dce3e8}.exercise-id{background:#f8edef;color:#a52e38;border-color:#d8b8be}.interpretation{background:#f8edef}.interpretation h3,.interpretation p{color:#344e61}footer{color:#647586}}
'''
