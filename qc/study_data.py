"""Recompute the original 7 October 2026 PDF study from its raw evidence.

Adapted from the study's original analyze.py. No network or PDF-writing code.
The separately retained analysis.json is a frozen reference, never overwritten.
"""
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import datetime
import numpy as np

# Levin/Rubin Appendix Table 9, n=5; the attached PDF uses D4=2.114.
FACTORS = dict(n=5, d2=2.326, A2=.577, D3=0.0, D4=2.114)

def wilson(failures, total):
    """Two-sided 95% Wilson interval, with the independence caveat in report."""
    z = statistics.NormalDist().inv_cdf(.975); p = failures / total
    divisor = 1 + z*z/total
    center = (p + z*z/(2*total)) / divisor
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / divisor
    return max(0, center-half), min(1, center+half)

def validate_and_calculate(data, evidence):
    meta = json.loads((data/'metadata.json').read_text(encoding='utf-8'))
    products = json.loads((data/'products_snapshot.json').read_text(encoding='utf-8'))['products']
    with (data/'requests.csv').open(encoding='utf-8', newline='') as stream:
        raw = list(csv.DictReader(stream))
    if not all((evidence/name).exists() for name in ['ui_checks.json','cart_before_refresh.jpg','cart_after_refresh.jpg']):
        raise ValueError('This combined report needs the bundled UI checks and two cart screenshots. Use the supplied evidence folder.')
    ui = json.loads((evidence/'ui_checks.json').read_text(encoding='utf-8'))
    if not ui:
        raise ValueError('The UI evidence list is empty.')
    if not meta.get('collection_finished_pk'):
        raise ValueError('Collection is incomplete. Finish collecting before analysis.')
    if len(raw) != meta['measured_requests'] or len({r['request_id'] for r in raw}) != len(raw):
        raise ValueError('Request count or unique IDs disagree with metadata.')
    if [int(r['request_id']) for r in raw] != list(range(1, len(raw)+1)):
        raise ValueError('Request IDs must form the original consecutive sequence.')
    stamps = [datetime.fromisoformat(r['timestamp_pk']) for r in raw]
    if stamps != sorted(stamps):
        raise ValueError('Request timestamps are not chronological.')
    for r in raw:
        if r['passed'] not in {'True', 'False'}:
            raise ValueError('Unknown pass/fail value.')
        t = float(r['elapsed_ms'])
        if not math.isfinite(t) or t <= 0:
            raise ValueError('Invalid elapsed time.')
        if len(r['sha256']) != 64:
            raise ValueError('Missing response hash.')
        if r['passed'] == 'True':
            expected = '401' if r['feature'] == 'Anonymous access protection' else '200'
            if r['http_status'] != expected:
                raise ValueError('A passing observation has an unexpected HTTP status.')
        if r['study'] not in {'micro','macro'}:
            raise ValueError('Unknown study label.')
    micro = [r for r in raw if r['study']=='micro']
    macro = [r for r in raw if r['study']=='macro']
    if len(micro) != meta['micro_batches']*5 or len(macro) != meta['macro_batches']*5:
        raise ValueError('The recorded sample sizes disagree with the protocol.')
    group_rows, complete, omitted = [], [], []
    for batch in range(1, meta['micro_batches']+1):
        rows = [r for r in micro if int(r['batch'])==batch]
        if sorted(int(r['repeat']) for r in rows) != [1,2,3,4,5]:
            raise ValueError('Micro group does not contain all five intended attempts.')
        if all(r['passed']=='True' for r in rows):
            complete.append(batch)
            a = np.array([float(r['elapsed_ms']) for r in rows], dtype=float)
            mean, span = float(a.mean()), float(np.ptp(a))
            # Independent direct calculations protect against array/axis errors.
            if not math.isclose(mean, statistics.mean(a.tolist()), rel_tol=1e-12):
                raise ValueError('Independent mean calculation failed.')
            if not math.isclose(span, max(a)-min(a), abs_tol=1e-10):
                raise ValueError('Independent range calculation failed.')
            row = dict(batch=batch, timestamp_pk=rows[0]['timestamp_pk'])
            row.update({f't{i+1}_ms':float(a[i]) for i in range(5)})
            row.update(mean_ms=mean,range_ms=span)
            group_rows.append(row)
        else:
            # Retain failed attempts in raw CSV. A five-observation Xbar/R group
            # cannot be created from fewer than five successful measurements.
            omitted.append(batch)
    if len(group_rows)<5:
        raise ValueError('Too few complete successful groups for this baseline.')
    means = np.array([r['mean_ms'] for r in group_rows]); spans = np.array([r['range_ms'] for r in group_rows])
    grand, rbar = float(means.mean()), float(spans.mean())
    half = 3*rbar/(FACTORS['d2']*math.sqrt(5))
    limits = dict(xbar_cl=grand,xbar_lcl=grand-half,xbar_ucl=grand+half,
                  range_cl=rbar,range_lcl=FACTORS['D3']*rbar,range_ucl=FACTORS['D4']*rbar,
                  sigma_estimate=rbar/FACTORS['d2'])
    for r in group_rows:
        r['mean_signal'] = r['mean_ms']<limits['xbar_lcl'] or r['mean_ms']>limits['xbar_ucl']
        r['range_signal'] = r['range_ms']<limits['range_lcl'] or r['range_ms']>limits['range_ucl']
    # Alternative rounded A2 calculation should be close, but not identical.
    # The actual chart uses the book's d2 formula (Equation 10-2).
    alt_half = FACTORS['A2']*rbar
    successful = np.array([float(r['elapsed_ms']) for r in micro if r['passed']=='True'])
    q1, med, q3, p95, p99 = np.percentile(successful,[25,50,75,95,99])
    fences = (float(q1-1.5*(q3-q1)),float(q3+1.5*(q3-q1)))
    summary = dict(count=len(micro),successful=len(successful),failures=len(micro)-len(successful),
                   complete_groups=len(group_rows),omitted_groups=omitted,min_ms=float(successful.min()),
                   max_ms=float(successful.max()),mean_ms=float(successful.mean()),median_ms=float(med),
                   p95_ms=float(p95),p99_ms=float(p99),sample_sd_ms=float(successful.std(ddof=1)),
                   q1_ms=float(q1),q3_ms=float(q3),tukey_low_ms=fences[0],tukey_high_ms=fences[1],
                   tukey_outliers=int(((successful<fences[0])|(successful>fences[1])).sum()),
                   mean_signals=[r['batch'] for r in group_rows if r['mean_signal']],
                   range_signals=[r['batch'] for r in group_rows if r['range_signal']],
                   halfwidth_d2_ms=half,halfwidth_rounded_A2_ms=alt_half,limits=limits)
    if not math.isclose(grand, statistics.mean(r['mean_ms'] for r in group_rows), rel_tol=1e-12):
        raise ValueError('Grand mean check failed.')
    macro_groups=[]; features=[c['feature'] for c in meta['macro_check_definitions']]
    for batch in range(1,meta['macro_batches']+1):
        rows=[r for r in macro if int(r['batch'])==batch]
        if Counter(r['feature'] for r in rows)!=Counter(features):
            raise ValueError('Macro round does not contain the fixed five checks.')
        d=sum(r['passed']=='False' for r in rows)
        macro_groups.append(dict(batch=batch,checks=len(rows),failures=d,proportion_failed=d/len(rows)))
    total=len(macro); failures=sum(r['passed']=='False' for r in macro); pbar=failures/total
    p_half=3*math.sqrt(pbar*(1-pbar)/5)
    p_limits=dict(cl=pbar,lcl=max(0,pbar-p_half),ucl=min(1,pbar+p_half))
    for r in macro_groups:
        r['outside_limits']=r['proportion_failed']<p_limits['lcl'] or r['proportion_failed']>p_limits['ucl']
    intervals=wilson(failures,total)
    feature_stats=[]
    for feature in features:
        rows=[r for r in macro if r['feature']==feature]
        vals=[float(r['elapsed_ms']) for r in rows if r['passed']=='True']
        feature_stats.append(dict(feature=feature,attempts=len(rows),passed=sum(r['passed']=='True' for r in rows),
                                  failed=sum(r['passed']=='False' for r in rows),
                                  expected_status=401 if feature=='Anonymous access protection' else 200,
                                  median_ms=float(np.median(vals)) if vals else None,
                                  p95_ms=float(np.percentile(vals,95)) if vals else None))
    crows=[]; catalog_issues=[]; ids=set()
    for p in products:
        if p['_id'] in ids:catalog_issues.append('Duplicate product ID '+p['_id'])
        ids.add(p['_id'])
        for field in ['productName','category','subCategory','description']:
            if not isinstance(p.get(field),str) or not p[field].strip():catalog_issues.append(p['_id']+' missing '+field)
        price=p.get('price')
        if isinstance(price,bool) or not isinstance(price,(int,float)) or price<0:catalog_issues.append(p['_id']+' invalid price')
        if not isinstance(p.get('size'),list) or not p['size']:catalog_issues.append(p['_id']+' missing sizes')
        if not isinstance(p.get('image'),list) or not p['image']:catalog_issues.append(p['_id']+' missing image URLs')
        crows.append(dict(product_id=p['_id'],product_name=p.get('productName',''),category=p.get('category',''),
                          subcategory=p.get('subCategory',''),price=price,sizes=' | '.join(p.get('size',[])),
                          image_count=len(p.get('image',[])),best_seller=p.get('bestSeller'),
                          created_at=p.get('createdAt'),updated_at=p.get('updatedAt'),
                          product_page=meta['site']+'/product/'+p['_id']))
    prices=np.array([float(p['price']) for p in products])
    category=Counter(p['category'] for p in products)
    if sum(category.values())!=len(products):raise ValueError('Catalog counts do not sum correctly.')
    hashes={name:hashlib.sha256((data/name).read_bytes()).hexdigest()
            for name in ['requests.csv','metadata.json','products_snapshot.json','discovery.json']}
    if (evidence/'ui_checks.json').exists():hashes['evidence/ui_checks.json']=hashlib.sha256((evidence/'ui_checks.json').read_bytes()).hexdigest()
    validation=dict(result='PASS',raw_files_sha256=hashes,checks=[
        'Metadata, row counts, unique sequential request IDs and chronological timestamps agree.',
        'Every attempt has a finite positive time, pass/fail label and response SHA-256.',
        'All passing statuses satisfy the expected contract; expected 401 is a pass.',
        'All micro groups and all fixed macro rounds are structurally complete.',
        'NumPy subgroup means and ranges agree with independent direct calculations.',
        'Grand mean independently recomputed; catalog category counts sum to total.',
        'Failed attempts retained; incomplete latency groups explicitly listed.',
        'Book n=5 factors used: d2=2.326, D3=0, D4=2.114; d2 formula defines Xbar limits.'
    ])
    analysis=dict(metadata=meta,book_factors=FACTORS,micro=summary,micro_groups=group_rows,
                  macro=dict(attempts=total,failures=failures,passed=total-failures,pbar=pbar,limits=p_limits,
                             wilson_95_interval=list(intervals),failure_categories=dict(Counter(r['failure_category'] for r in macro if r['passed']=='False')),
                             features=feature_stats,groups=macro_groups),
                  catalog=dict(count=len(products),unique_ids=len(ids),categories=dict(category),
                               subcategories=dict(Counter(p['subCategory'] for p in products)),
                               min_price=float(prices.min()),max_price=float(prices.max()),
                               mean_price=float(prices.mean()),median_price=float(np.median(prices)),
                               issues=catalog_issues,checks_scope='Field presence/types, nonnegative prices, unique IDs; image URLs are present but not each downloaded.'),
                  ui=dict(count=len(ui),passed=sum(r['passed'] for r in ui),failed=sum(not r['passed'] for r in ui),checks=ui),
                  validation=validation)
    return analysis, raw, crows
