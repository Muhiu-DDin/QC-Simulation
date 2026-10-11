"""PDF-aligned ForeverMart analysis and reproducible group bootstrap simulations."""
from __future__ import annotations

import base64
from html import escape
import json
import math
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from scipy import stats

from .dataset_projects import _image, _number, _simulate, PLOT_LOCK
from .study_data import FACTORS, validate_and_calculate

STUDY = Path(__file__).resolve().parents[1] / 'data/forevermart_study'
RAW_COLUMNS = ('period', 't1_ms', 't2_ms', 't3_ms', 't4_ms', 't5_ms')
RED, INK, BLUE = '#bd3039', '#292c34', '#426a86'
LIMIT_LABELS = dict(xbar_lcl='Mean chart · lower limit', xbar_cl='Mean chart · center',
                    xbar_ucl='Mean chart · upper limit', range_lcl='Range chart · lower limit',
                    range_cl='Range chart · center', range_ucl='Range chart · upper limit')


def validate_micro_rows(rows):
    """Five individual successful timings are required; never invent ranges."""
    if not isinstance(rows, list) or not 5 <= len(rows) <= 500:
        raise ValueError('For a raw micro study, supply 5–500 groups of five successful response times.')
    cleaned, seen = [], set()
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != set(RAW_COLUMNS):
            raise ValueError(f'Micro row {i} needs exactly: {",".join(RAW_COLUMNS)}.')
        period = str(row['period']).strip() if row['period'] is not None else ''
        if not period or len(period) > 100 or period in seen:
            raise ValueError(f'Micro row {i} needs a unique period label of 1–100 characters.')
        seen.add(period)
        cleaned.append(dict(period=period, **{key: _number(row[key], f'Row {i}: {key}', minimum=1e-9)
                                             for key in RAW_COLUMNS[1:]}))
    return cleaned


def micro_analysis(rows):
    rows = validate_micro_rows(rows)
    values = np.array([[row[key] for key in RAW_COLUMNS[1:]] for row in rows])
    means, spans = values.mean(axis=1), np.ptp(values, axis=1)
    grand, rbar = float(means.mean()), float(spans.mean())
    half = 3 * rbar / (FACTORS['d2'] * math.sqrt(5))
    limits = dict(xbar_cl=grand, xbar_lcl=grand-half, xbar_ucl=grand+half,
                  range_cl=rbar, range_lcl=0., range_ucl=FACTORS['D4']*rbar,
                  sigma_estimate=rbar/FACTORS['d2'])
    q1, med, q3, p95, p99 = np.percentile(values, [25, 50, 75, 95, 99])
    lo, hi = q1-1.5*(q3-q1), q3+1.5*(q3-q1)
    groups = [dict(batch=i+1, period=row['period'], **{key: row[key] for key in RAW_COLUMNS[1:]},
                   mean_ms=float(means[i]), range_ms=float(spans[i]),
                   mean_signal=bool(means[i] < limits['xbar_lcl'] or means[i] > limits['xbar_ucl']),
                   range_signal=bool(spans[i] > limits['range_ucl'])) for i, row in enumerate(rows)]
    summary = dict(count=int(values.size), successful=int(values.size), failures=0, complete_groups=len(rows),
                   omitted_groups=[], min_ms=float(values.min()), max_ms=float(values.max()),
                   mean_ms=grand, median_ms=float(med), p95_ms=float(p95), p99_ms=float(p99),
                   sample_sd_ms=float(values.std(ddof=1)), q1_ms=float(q1), q3_ms=float(q3),
                   tukey_low_ms=float(lo), tukey_high_ms=float(hi),
                   tukey_outliers=int(((values < lo) | (values > hi)).sum()),
                   mean_signals=[g['batch'] for g in groups if g['mean_signal']],
                   range_signals=[g['batch'] for g in groups if g['range_signal']],
                   halfwidth_d2_ms=half, halfwidth_rounded_A2_ms=FACTORS['A2']*rbar, limits=limits)
    return summary, groups, values


def bootstrap_groups(values, trials, seed, *, micro):
    """Resample entire groups, retaining their within-group measured observations.

    The percentile interval is an exploratory group-bootstrap interval. The
    separate MC interval describes numerical simulation noise, not study risk.
    Chunking bounds memory even for 500 groups and 100,000 trials.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[1] != 5 or len(values) < 2:
        raise ValueError('Group resampling requires at least two complete groups of five timings.')
    means, ranges = values.mean(axis=1), np.ptp(values, axis=1)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2 if micro else 3]))
    averages, spreads = np.empty(trials), np.empty(trials)
    example_indices = None
    for start in range(0, trials, 1024):
        stop = min(start+1024, trials)
        selected = rng.integers(0, len(values), size=(stop-start, len(values)))
        if example_indices is None:
            example_indices = selected[0].tolist()
        averages[start:stop] = means[selected].mean(axis=1)
        spreads[start:stop] = ranges[selected].mean(axis=1)
    target, estimate = float(means.mean()), float(averages.mean())
    standard_error = float(averages.std(ddof=1))
    mc_error = standard_error / math.sqrt(trials)
    margin = float(stats.norm.ppf(.995))*mc_error
    low, high = np.percentile(averages, [2.5, 97.5])
    result = dict(method='whole-group percentile bootstrap', trials=trials, seed=seed,
                  groups_per_trial=len(values), checks_per_group=5,
                  recorded_mean_ms=target, simulated_mean_ms=estimate,
                  bootstrap_standard_error_ms=standard_error,
                  exploratory_ci95_low_ms=float(low), exploratory_ci95_high_ms=float(high),
                  mean_mc_standard_error_ms=mc_error,
                  mean_mc_ci99_low_ms=estimate-margin, mean_mc_ci99_high_ms=estimate+margin,
                  recorded_mean_within_mc_ci99=bool(estimate-margin <= target <= estimate+margin),
                  absolute_mean_difference_ms=abs(estimate-target),
                  example_selected_groups=[i+1 for i in example_indices],
                  example_trial_mean_ms=float(averages[0]),
                  first_ten_trial_means_ms=averages[:10].tolist(),
                  assumption='Whole groups are sampled with replacement and treated as independent, comparable groups. Serial correlation and changing variability can invalidate population inference; these are exploratory sensitivity results, not new website measurements.')
    if micro:
        width = 3*spreads/(FACTORS['d2']*math.sqrt(5))
        distributions = dict(xbar_cl=averages, xbar_lcl=averages-width, xbar_ucl=averages+width,
                             range_cl=spreads, range_lcl=np.zeros(trials), range_ucl=FACTORS['D4']*spreads)
        result['control_limit_sensitivity'] = {
            name: dict(simulated_mean_ms=float(draws.mean()), ci95_low_ms=float(np.percentile(draws, 2.5)),
                       ci95_high_ms=float(np.percentile(draws, 97.5))) for name, draws in distributions.items()}
    return result, averages


def _equal(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(actual) == set(expected) and all(_equal(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(_equal(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9)
    return actual == expected


def load_study():
    analysis, raw, catalog = validate_and_calculate(STUDY, STUDY/'evidence')
    frozen = json.loads((STUDY/'analysis.json').read_text(encoding='utf-8'))
    audit = json.loads((STUDY/'validation.json').read_text(encoding='utf-8'))
    if analysis['validation']['raw_files_sha256'] != audit['raw_files_sha256']:
        raise ValueError('The original study evidence has changed. Restore the dated source files before comparing with the PDF.')
    matches = {key: _equal(analysis[key], frozen[key]) for key in ['micro', 'micro_groups', 'macro', 'catalog', 'ui']}
    return analysis, raw, catalog, frozen, matches


def _table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{escape(str(x))}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(x))}</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def _f(value, digits=2):
    return f'{value:,.{digits}f}'


def _plot_style(ax):
    ax.grid(axis='y', alpha=.15)
    ax.spines[['top', 'right']].set_visible(False)


def study_plots(scale, analysis, raw, values, draws, bootstrap, threshold):
    plots = {}
    with PLOT_LOCK:
        if scale == 'micro':
            summary, groups = analysis['micro'], analysis['micro_groups']
            limits = summary['limits']
            fig = Figure(figsize=(10, 6.5), constrained_layout=True)
            axes = fig.subplots(2, 1, sharex=True)
            x = np.arange(1, len(groups)+1)
            for ax, key, prefix, title in zip(axes, ['mean_ms', 'range_ms'], ['xbar', 'range'], ['Mean chart (X̄)', 'Range chart (R)']):
                y = np.array([g[key] for g in groups])
                ax.plot(x, y, 'o-', color=BLUE, linewidth=1.2, markersize=3.5)
                for suffix, name, style, color in [('cl', 'Center', '-', INK), ('lcl', 'Lower limit', '--', RED), ('ucl', 'Upper limit', '--', RED)]:
                    limit = limits[f'{prefix}_{suffix}']
                    ax.axhline(limit, color=color, linestyle=style, linewidth=1, label=f'{name}: {limit:.2f}')
                flagged = (y < limits[f'{prefix}_lcl']) | (y > limits[f'{prefix}_ucl'])
                ax.scatter(x[flagged], y[flagged], color=RED, s=40, zorder=3)
                ax.set_ylabel('Milliseconds')
                ax.set_title(title, pad=34)
                _plot_style(ax)
                ax.legend(fontsize=8, ncol=3, loc='lower right', bbox_to_anchor=(1, 1.01))
            axes[1].set_xlabel('Recorded group (five consecutive catalog requests)')
            axes[1].set_xticks(np.arange(1, len(groups)+1) if len(groups) <= 30 else np.linspace(1, len(groups), 15, dtype=int))
            plots['control'] = ('Recorded data · mean and range charts', _image(fig))
            fig = Figure(figsize=(10, 4), constrained_layout=True)
            left, right = fig.subplots(1, 2)
            individual = values.ravel()
            left.hist(individual, bins='fd', color=BLUE, edgecolor='white')
            left.axvline(summary['median_ms'], color=INK, linestyle='--', label='Median')
            left.axvline(summary['p95_ms'], color=RED, linestyle='--', label='95th percentile')
            left.set(xlabel='Individual response time (ms)', ylabel='Requests', title='All recorded catalog timings')
            left.legend(fontsize=8)
            right.plot(np.arange(1, len(individual)+1), individual, color=BLUE, linewidth=1, marker='.', markersize=3)
            right.set(xlabel='Request order', ylabel='Milliseconds', title='Time sequence')
            if threshold is not None:
                right.axhline(threshold, color=RED, linestyle='--', label='Your optional target')
                right.legend(fontsize=8)
            for ax in [left, right]:
                _plot_style(ax)
            plots['timing'] = ('Recorded data · latency distribution and sequence', _image(fig))
        else:
            macro = analysis['macro']
            fig = Figure(figsize=(10, 3.7), constrained_layout=True)
            ax = fig.subplots()
            ax.plot([g['batch'] for g in macro['groups']], [g['proportion_failed']*100 for g in macro['groups']], 'o-', color=BLUE, markersize=4, label='Recorded failures')
            for name, style in [('cl', '-'), ('lcl', '--'), ('ucl', '--')]:
                ax.axhline(macro['limits'][name]*100, color=RED if name != 'cl' else INK, linestyle=style, linewidth=1, label=name.upper())
            ax.set(xlabel='Round (same five service checks)', ylabel='Failed checks (%)', title='Recorded failure-rate chart', ylim=(-.2, 1))
            ax.text(.5, .55, '0 failures in 100 service checks\nZero observed failures does not prove zero future risk.', transform=ax.transAxes, ha='center', color=INK)
            ax.legend(fontsize=8, ncol=4, loc='upper right')
            _plot_style(ax)
            plots['control'] = ('Recorded data · macro failure-rate chart', _image(fig))
            fig = Figure(figsize=(10, 4.5), constrained_layout=True)
            ax = fig.subplots()
            feature_times = [[float(r['elapsed_ms']) for r in raw if r['study'] == 'macro' and r['feature'] == feature['feature'] and r['passed'] == 'True'] for feature in macro['features']]
            ax.boxplot(feature_times, tick_labels=['HTML', 'JavaScript', 'Catalog', 'Product detail', 'Access protection'],
                       showfliers=True, patch_artist=True, boxprops=dict(facecolor='#edf2f6', color=INK),
                       medianprops=dict(color=RED, linewidth=1.4), whiskerprops=dict(color=INK), capprops=dict(color=INK))
            ax.set(ylabel='Request duration (ms)', title='Service timings · twenty observations per service')
            if threshold is not None:
                ax.axhline(threshold, color=RED, linestyle='--', label='Your optional target')
                ax.legend(fontsize=8)
            _plot_style(ax)
            plots['endpoints'] = ('Recorded data · performance by service', _image(fig))
        if 'catalog' in analysis:
            fig = Figure(figsize=(10, 3.8), constrained_layout=True)
            left, right = fig.subplots(1, 2)
            categories = analysis['catalog']['categories']
            bars = left.bar(list(categories), list(categories.values()), color=BLUE)
            left.bar_label(bars, padding=3)
            left.set(title='Recorded catalog categories', ylabel='Products', ylim=(0, max(categories.values())*1.3))
            right.hist([float(p['price']) for p in analysis['products']], bins=8, color=RED, edgecolor='white')
            right.set(title='Recorded catalog prices', xlabel='Listed price (currency code unspecified)', ylabel='Products')
            for ax in [left, right]:
                _plot_style(ax)
            plots['catalog'] = ('Recorded data · catalog exploration', _image(fig))
        fig = Figure(figsize=(10, 4), constrained_layout=True)
        ax = fig.subplots()
        if float(np.ptp(draws)) == 0:
            ax.axvline(bootstrap['recorded_mean_ms'], color=BLUE, linewidth=3, label='Every resampled mean is identical')
        else:
            ax.hist(draws, bins=40, color=BLUE, edgecolor='white', label='Simulated study means')
        ax.axvline(bootstrap['recorded_mean_ms'], color=RED, linewidth=1.5, label=f'Recorded mean: {bootstrap["recorded_mean_ms"]:.2f} ms')
        ax.axvline(bootstrap['exploratory_ci95_low_ms'], color=INK, linestyle='--', label='Exploratory 95% bootstrap interval')
        ax.axvline(bootstrap['exploratory_ci95_high_ms'], color=INK, linestyle='--')
        ax.set(xlabel='Mean of one resampled study (ms)', ylabel='Simulation trials', title=f'Simulation · {bootstrap["trials"]:,} resampled studies')
        ax.legend(fontsize=8)
        _plot_style(ax)
        plots['bootstrap'] = ('Simulation output · resampled study means', _image(fig))
    return plots


STYLE = '''body{margin:0;background:#f0f1f4;color:#292c34;font:16px/1.65 Arial,sans-serif}main{max-width:1060px;margin:auto;padding:24px}header{background:#292c34;color:white;padding:32px;border-top:5px solid #bd3039}header p{color:#e4c1c3}h1{font-size:30px;line-height:1.3;margin:8px 0}h2{font-size:23px;margin:0 0 16px}h3{font-size:18px}section{background:white;margin:18px 0;padding:28px;border:1px solid #dce0e5}p{margin:12px 0}.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:1.6px}.muted{color:#5d6775;font-size:14px}.notice{padding:16px 20px;border-left:4px solid #bd3039;background:#fbf3f4}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card{background:#f4f6f8;border-top:3px solid #bd3039;padding:18px}.card strong{display:block;font-size:27px}.card span{font-size:13px;color:#5d6775}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:11px 12px;border-bottom:1px solid #dce0e5;vertical-align:top}thead{background:#292c34;color:white}tbody tr:nth-child(even){background:#f5f6f8}img{max-width:100%;height:auto;display:block;margin:18px auto}code{font-size:14px;overflow-wrap:anywhere}details{margin:20px 0}summary{cursor:pointer;font-weight:bold}a{color:#9d2530}@media(max-width:650px){main,section{padding:14px}.cards{grid-template-columns:1fr}header{padding:20px}h1{font-size:25px}}@media print{body{background:white}main{padding:0}section{break-inside:avoid}details{display:block}summary{display:none}}'''


def study_report(record, analysis, plots):
    scale = record['case']['inputs']['scale']
    own = record['case']['inputs']['dataset_source'] == 'own'
    result, bootstrap = record['calculated'], record['simulation']['group_bootstrap']
    source = 'Independent uploaded timings' if own else 'ForeverMart · attached PDF study · 7 October 2026'
    sections = []
    def section(title, content):
        sections.append(f'<section><h2>{title}</h2>{content}</section>')
    if scale == 'micro':
        cards = [('Recorded requests', str(result['count'])), ('Mean response time', _f(result['mean_ms'])+' ms'), ('95th percentile', _f(result['p95_ms'])+' ms')]
        section('Measured performance', '<div class="cards">'+''.join(f'<div class="card"><span>{name}</span><strong>{value}</strong></div>' for name, value in cards)+'</div>'+
                _table(['Statistic', 'Recorded value'], [('Groups × requests', f'{result["complete_groups"]} × 5'), ('Median', _f(result['median_ms'])+' ms'), ('99th percentile', _f(result['p99_ms'])+' ms'), ('Minimum / maximum', _f(result['min_ms'])+' / '+_f(result['max_ms'])+' ms'), ('Sample standard deviation', _f(result['sample_sd_ms'])+' ms'), ('Tukey outliers (1.5 × IQR)', result['tukey_outliers'])]))
        limits = result['limits']
        section('Quality-control calculations', _table(['Chart', 'Lower limit (ms)', 'Center (ms)', 'Upper limit (ms)', 'Flagged groups'],
            [(name, _f(limits[prefix+'_lcl']), _f(limits[prefix+'_cl']), _f(limits[prefix+'_ucl']), ', '.join(map(str, result[signals])) or 'None')
             for name, prefix, signals in [('Mean (X̄)', 'xbar', 'mean_signals'), ('Range (R)', 'range', 'range_signals')]])+
            '<p class="notice">These are exploratory Phase I charts. Investigate the timing spikes and changing within-group spread before treating this baseline as stable. A chart signal is not a confirmed software defect or an SLA failure.</p>')
    else:
        cards = [('Recorded service checks', str(result['attempts'])), ('Passed / failed', f'{result["passed"]} / {result["failures"]}'), ('Observed failure rate', _f(result['pbar']*100)+'%')]
        section('Service-check results', '<div class="cards">'+''.join(f'<div class="card"><span>{name}</span><strong>{value}</strong></div>' for name, value in cards)+'</div>'+
                _table(['Statistic', 'Recorded value'], [('Fixed rounds', len(result['groups'])), ('Checks per round', 5), ('p-chart LCL / CL / UCL', ' / '.join(_f(result['limits'][k]*100)+'%' for k in ['lcl', 'cl', 'ucl'])), ('Illustrative pooled 95% Wilson interval', '–'.join(_f(x*100)+'%' for x in result['wilson_95_interval']))])+
                '<p class="notice">All 100 recorded service checks passed. This does not prove that shopping, checkout or every browser interaction works. The five checks have different purposes; the pooled Wilson interval assumes independent, comparable outcomes and is only an illustrative bound for this fixed suite.</p>')
        definitions = analysis['metadata']['macro_check_definitions']
        section('The same five checks in every round', _table(['Service', 'Expected outcome', 'Pass / fail', 'Median (ms)', 'P95 (ms)'],
            [(f['feature'], d['expected'], f'{f["passed"]} / {f["failed"]}', _f(f['median_ms']), _f(f['p95_ms'])) for f, d in zip(result['features'], definitions)])+
            '<p>HTTP 401 is a <strong>pass</strong> for anonymous access protection: an unauthenticated request is supposed to be rejected. Timings include network, TLS and response download; they do not measure browser rendering.</p>')
    comparison = record['comparisons']['pdf_study']
    if not own:
        section('Comparison with the attached PDF study', '<p>Calculations use the original full-precision measurements. The retained study answers are independent of this calculation run; the displayed PDF rounds timings to two decimal places.</p>'+_table(['Result', 'Stored study value', 'Calculated value', 'Check'], comparison['fields'])+f'<p><strong>Complete source comparison: {comparison["status"]}.</strong> Raw-file hashes, all micro groups, macro rounds, catalog statistics and UI counts were checked against the retained study files.</p>')
    for key, (title, url) in plots.items():
        if key != 'bootstrap':
            section(title, f'<img src="{url}" alt="{escape(title)}"><p class="muted">This chart uses recorded data. It is not generated by the random simulation.</p>')
    section('Simulation · resampling the recorded groups',
        f'<p>For one simulation, Python randomly picks <strong>{bootstrap["groups_per_trial"]} recorded groups</strong>, allowing the same group to be picked more than once. Each picked group keeps its original five timings. Python calculates the average of the resulting {bootstrap["groups_per_trial"]*5} timings. It repeats this process <strong>{bootstrap["trials"]:,} times</strong>.</p>'+
        '<p>This asks: how much would the study average move if we obtained another selection of groups like the recorded ones? It reuses real observations; it does not send new requests to ForeverMart.</p>'+
        _table(['Simulation result', 'Value'], [('Recorded mean', _f(bootstrap['recorded_mean_ms'])+' ms'), ('Average of simulated study means', _f(bootstrap['simulated_mean_ms'])+' ms'), ('Absolute difference', _f(bootstrap['absolute_mean_difference_ms'], 4)+' ms'), ('Exploratory 95% bootstrap interval', _f(bootstrap['exploratory_ci95_low_ms'])+'–'+_f(bootstrap['exploratory_ci95_high_ms'])+' ms'), ('Spread of simulated means (bootstrap SE)', _f(bootstrap['bootstrap_standard_error_ms'])+' ms'), ('99% interval for Monte Carlo mean error', _f(bootstrap['mean_mc_ci99_low_ms'])+'–'+_f(bootstrap['mean_mc_ci99_high_ms'])+' ms'), ('Fixed random seed', bootstrap['seed'])])+
        f'<img src="{plots["bootstrap"][1]}" alt="Distribution of simulated study averages">'+
        '<p class="notice">The 95% interval describes sensitivity to group selection under the independent-group assumption. The separate 99% Monte Carlo interval describes numerical simulation noise. Serial measurements and unstable variability limit population conclusions. Neither interval establishes a website performance guarantee.</p>'+
        '<details><summary>See the first simulated study</summary><p>Picked group numbers: '+escape(', '.join(map(str, bootstrap['example_selected_groups'])))+f'.</p><p>Its average: {_f(bootstrap["example_trial_mean_ms"])} ms. The group numbers refer to the recorded input table below.</p></details>')
    if scale == 'micro':
        section('Simulation · sensitivity of the control limits', _table(['Limit', 'Recorded (ms)', 'Average simulated value (ms)', 'Exploratory 95% interval (ms)'],
            [(LIMIT_LABELS[name], _f(result['limits'][name]), _f(row['simulated_mean_ms']), _f(row['ci95_low_ms'])+'–'+_f(row['ci95_high_ms'])) for name, row in bootstrap['control_limit_sensitivity'].items()])+
            '<p>Each simulated study recalculates its mean, average range and chart limits using the same book factors. These simulated limits show baseline sensitivity; the recorded-data chart continues to use its original limits.</p>')
    else:
        model = record['simulation']['failure_model']
        section('Simulation · checking the failure-count formula', '<p>The observed failure rate is 0%. A binomial model fitted directly to that rate produces zero failures in every simulated five-check round. This boundary result is expected; it cannot discover failures absent from the sample.</p>'+_table(['Model verification', 'Value'], [('Checks in one simulated round', model['representative_batch_size']), ('Simulated rounds', f'{model["trials"]:,}'), ('Exact probability outside p-chart limits', _f(model['exact_outside_probability']*100)+'%'), ('Monte Carlo probability outside limits', _f(model['simulated_outside_probability']*100)+'%'), ('Absolute probability difference', model['absolute_error'])])+
            '<p>Do not interpret this as “the website can never fail.” More real coverage and later measurements are needed. Bootstrap timing simulation above remains useful because the recorded response times vary.</p>')
    if not own:
        catalog = analysis['catalog']
        section('Catalog snapshot checks', _table(['Check', 'Recorded result'], [('Products / unique IDs', f'{catalog["count"]} / {catalog["unique_ids"]}'), ('Categories', ', '.join(f'{k}: {v}' for k, v in catalog['categories'].items())), ('Minimum / maximum listed price', _f(catalog['min_price'])+' / '+_f(catalog['max_price'])), ('Mean / median listed price', _f(catalog['mean_price'])+' / '+_f(catalog['median_price'])), ('Field validation issues', len(catalog['issues']))])+'<p class="muted">Checks cover field presence/types, unique IDs, nonnegative prices and nonempty size/image lists. Image URLs were present; every image was not downloaded.</p>')
        if scale == 'macro':
            ui = analysis['ui']
            section('Separate browser checks · 13 passed, 2 study-criterion issues', '<p>These 15 browser checks are reported separately from the 100 service checks. They are recorded evidence from the PDF study, not new tests executed by this simulation.</p>'+_table(['ID', 'Check', 'Observed result', 'Outcome'], [(r['id'], r['test'], r['observed'], 'Passed' if r['passed'] else 'Issue') for r in ui['checks']])+
                _table(['Issue', 'Corrective action', 'Retest'], [('UI13 · product name missing from cart line', 'Display the product name and link beside its selected size, price and quantity.', 'Add two different products; verify each row is identifiable and opens the correct product.'), ('UI15 · guest cart disappears after refresh', 'Persist validated product IDs, sizes and quantities locally; restore and reprice from the catalog. Merge safely on login.', 'Add two size-M units, refresh, and verify quantity 2 and total 410 before testing update/removal and login merge.')])+
                '<p class="muted">These issues use the study’s stated usability criteria; a formal product requirements specification was not supplied. They are not added to the service failure count.</p>')
            before = base64.b64encode((STUDY/'evidence/cart_before_refresh.jpg').read_bytes()).decode('ascii')
            after = base64.b64encode((STUDY/'evidence/cart_after_refresh.jpg').read_bytes()).decode('ascii')
            section('Recorded cart evidence', f'<h3>Before refresh</h3><img src="data:image/jpeg;base64,{before}" alt="Recorded guest cart before refresh, quantity two and total 410"><h3>After refresh</h3><img src="data:image/jpeg;base64,{after}" alt="Recorded guest cart after refresh, empty cart and zero total"><p class="muted">Original screenshots accompanying UI13 and UI15 in the PDF study. They were not captured during this simulation run.</p>')
    threshold = record['case']['inputs']['specification_ms']
    if threshold is not None:
        section('Your optional performance target', f'<p>Your target is <strong>{_f(threshold)} ms</strong>. {record["target_exceedance_count"]} individual recorded request timings exceeded it. This is a user-supplied target, separate from statistical control limits and absent from the original PDF study.</p>')
    if scale == 'micro':
        rows = [(g.get('period', g['batch']), *[_f(g[k], 3) for k in RAW_COLUMNS[1:]], _f(g['mean_ms'], 3), _f(g['range_ms'], 3)) for g in analysis['micro_groups']]
        input_table = _table(['Group', 'Time 1', 'Time 2', 'Time 3', 'Time 4', 'Time 5', 'Mean', 'Range'], rows)
    else:
        input_table = _table(['Round', 'Checks', 'Failures', 'Failed proportion'], [(r['batch'], r['checks'], r['failures'], _f(r['proportion_failed']*100)+'%') for r in result['groups']])
    section('Recorded inputs and method', '<details><summary>View all recorded groups · timings in milliseconds</summary>'+input_table+'</details>'+
        '<h3>Calculation formulas</h3><p><code>Group mean = sum of its five timings / 5; group range = maximum − minimum.</code></p><p><code>X̄ limits = grand mean ± 3 × average range / (2.326 × √5).</code><br><code>R limits = 0 and 2.114 × average range.</code></p><p><code>p̄ = total failed / total checks; p limits = p̄ ± 3√[p̄(1−p̄)/5], clipped to 0–1.</code></p><p>Percentiles use NumPy’s linear interpolation; standard deviation uses the sample denominator (n−1). The n=5 chart factors match the attached study and Levin/Rubin’s book, including D4 = 2.114. All display rounding happens after calculation.</p>'+
        f'<p class="muted">{escape(source)}. No textbook-answer comparison is made for website measurements. Identical data, settings and seed reproduce the simulation; changing the seed changes random draws, not the recorded calculations.</p>'+
        '<p class="muted">Tools: Python, NumPy, SciPy and Matplotlib. References: original attached report.pdf and retained study evidence; Levin/Rubin, Statistics for Management, Chapter 10 / Appendix Table 9; <a href="https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm">NIST mean/range chart guidance</a>; <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html">SciPy bootstrap method documentation</a>.</p>')
    title = f'{scale.title()} study · ' + ('Independent timing analysis' if own else 'ForeverMart quality analysis')
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{scale.title()} study results</title><style>{STYLE}</style></head><body><main><header><span class="eyebrow">Software Testing · Data study and simulation</span><h1>{title}</h1><p>{escape(source)}</p></header>'+''.join(sections)+'</main></body></html>'


def evaluate_study(payload):
    scale = payload.get('scale', 'micro')
    if scale not in ('micro', 'macro'):
        raise ValueError('Dataset scale must be micro or macro.')
    source = payload.get('dataset_source', 'study')
    own = source == 'own'
    if source not in ('study', 'own') or (own and scale != 'micro'):
        raise ValueError('Raw five-timing uploads are supported for micro studies only.')
    if not own and 'rows' in payload:
        raise ValueError('Select your own dataset to analyze supplied rows.')
    trials = _number(payload.get('trials', 10000), 'Simulation trials', integral=True, minimum=100, maximum=100000)
    seed = _number(payload.get('seed', 20260901), 'Random seed', integral=True, maximum=2**32-1)
    threshold = payload.get('specification_ms')
    if threshold is not None:
        threshold = _number(threshold, 'Optional response-time target', minimum=1e-9)
    if own:
        cleaned = validate_micro_rows(payload.get('rows'))
        summary, groups, values = micro_analysis(cleaned)
        analysis = dict(micro=summary, micro_groups=groups)
        raw, frozen, matches = [], {}, {}
        provenance = dict(source='User-supplied individual response times', synthetic=False,
                          independently_verified=False)
    else:
        analysis, raw, catalog, frozen, matches = load_study()
        analysis['products'] = json.loads((STUDY/'products_snapshot.json').read_text(encoding='utf-8'))['products']
        summary = analysis[scale]
        selected = [r for r in raw if r['study'] == scale]
        values = np.array([[float(r['elapsed_ms']) for r in selected if int(r['batch']) == i]
                           for i in range(1, analysis['metadata'][scale+'_batches']+1)])
        cleaned = selected
        provenance = dict(source='Original attached PDF study', synthetic=False,
                          collected_at=analysis['metadata']['collection_started_pk'],
                          completed_at=analysis['metadata']['collection_finished_pk'],
                          request_timing=analysis['metadata']['request_timing'],
                          evidence_sha256=analysis['validation']['raw_files_sha256'],
                          source_comparison=matches, no_new_network_requests=True)
    bootstrap, draws = bootstrap_groups(values, trials, seed, micro=scale == 'micro')
    simulation = dict(group_bootstrap=bootstrap)
    if scale == 'macro':
        simulation['failure_model'] = _simulate(summary['pbar'], 5, trials, seed)
    fields = []
    if not own:
        reference = frozen[scale]
        if scale == 'micro':
            names = [('Requests', 'count'), ('Mean (ms)', 'mean_ms'), ('Median (ms)', 'median_ms'), ('P95 (ms)', 'p95_ms'), ('P99 (ms)', 'p99_ms'), ('Tukey outliers', 'tukey_outliers'), ('Mean-chart flagged groups', 'mean_signals'), ('Range-chart flagged groups', 'range_signals')]
            for label, key in names:
                fields.append([label, reference[key], summary[key], 'Verified' if _equal(summary[key], reference[key]) else 'Review'])
            for key in ['xbar_lcl', 'xbar_cl', 'xbar_ucl', 'range_lcl', 'range_cl', 'range_ucl']:
                fields.append([LIMIT_LABELS[key]+' (ms)', reference['limits'][key], summary['limits'][key], 'Verified' if _equal(summary['limits'][key], reference['limits'][key]) else 'Review'])
        else:
            for label, key in [('Service checks', 'attempts'), ('Passed checks', 'passed'), ('Failed checks', 'failures'), ('Failure proportion', 'pbar'), ('Wilson 95% interval', 'wilson_95_interval')]:
                fields.append([label, reference[key], summary[key], 'Verified' if _equal(summary[key], reference[key]) else 'Review'])
            for i, feature in enumerate(summary['features']):
                for key in ['median_ms', 'p95_ms']:
                    fields.append([feature['feature']+' · '+('Median (ms)' if key == 'median_ms' else 'P95 (ms)'), reference['features'][i][key], feature[key], 'Verified' if _equal(feature[key], reference['features'][i][key]) else 'Review'])
        # Keep full precision in JSON; round display only in the report table.
        for row in fields:
            for i in [1, 2]:
                if isinstance(row[i], float):
                    row[i] = _f(row[i], 6)
                elif isinstance(row[i], list):
                    row[i] = ', '.join(_f(x, 6) if isinstance(x, float) else str(x) for x in row[i])
    status = 'NOT_AVAILABLE' if own else 'Verified' if all(matches.values()) else 'Review required'
    comparisons = dict(book=dict(status='NOT_AVAILABLE', fields=[]), independent=dict(status='NOT_AVAILABLE', fields=[]),
                       pdf_study=dict(status=status, fields=fields))
    record = dict(case=dict(id=f'{scale}-pdf-study' if not own else 'micro-own-timings', kind='dataset',
                            title=f'{scale.title()} study and simulation',
                            inputs=dict(scale=scale, dataset_source=source, specification_ms=threshold, rows=cleaned)),
                  calculated=summary, simulation=simulation, comparisons=comparisons,
                  case_seed=seed, provenance=provenance,
                  target_exceedance_count=None if threshold is None else int((values > threshold).sum()))
    if not own:
        record['catalog'] = analysis['catalog']
        if scale == 'macro':
            record['ui'] = analysis['ui']
    plots = study_plots(scale, analysis, raw, values, draws, bootstrap, threshold)
    message = ('Independent uploaded micro timings. These are your own observations, not stored textbook or PDF-study data. No reference comparison is available.' if own else
               f'Original PDF study · 7 October 2026: {summary["count"] if scale == "micro" else summary["attempts"]} recorded {"catalog timings" if scale == "micro" else "service checks"}. PDF calculations: {status.lower()}. Simulation reuses these saved measurements; no new website checks are run.')
    return dict(category='independent', message=message, matched_exercises=[], record=record,
                report_html=study_report(record, analysis, plots))
