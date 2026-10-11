"""Independent software-test datasets: exploratory QC charts and model simulation.

One row is an ordered execution batch, not an individual defect. ``response_ms``
is the batch's mean response time; individual latency percentiles cannot be
recovered from these aggregates. Demo rows are synthetic, never collected data.
"""
from __future__ import annotations

import base64
import csv
from html import escape
from io import BytesIO
import json
import math
from pathlib import Path
import threading

import numpy as np
from scipy import stats
from matplotlib.figure import Figure

PLOT_LOCK = threading.Lock()
DEMO_SEED = 20260901
MAX_ROWS = 20000
REQUIRED_COLUMNS = ("period", "passed", "failed", "response_ms")
ROOT = Path(__file__).resolve().parents[1]


def _number(value, label, *, integral=False, minimum=0, maximum=1e9):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{label} must be a number.")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"{label} must be a number.") from None
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f"{label} must be finite and between {minimum:g} and {maximum:g}.")
    if integral and not result.is_integer():
        raise ValueError(f"{label} must be a whole number.")
    return int(result) if integral else result


def validate_rows(rows):
    """Validate ordered batch records without sorting or silently dropping rows."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("Provide at least one dataset row.")
    if len(rows) > MAX_ROWS:
        raise ValueError(f"Use at most {MAX_ROWS:,} dataset rows online.")
    cleaned = []
    seen = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or any(key not in row for key in REQUIRED_COLUMNS):
            raise ValueError(f"Row {index} needs period, passed, failed and response_ms.")
        period = str(row["period"]).strip() if row["period"] is not None else ""
        if not period or len(period) > 100:
            raise ValueError(f"Row {index}: period must contain 1–100 characters.")
        if period in seen:
            raise ValueError(f"Row {index}: period '{period}' is duplicated; use unique batch labels.")
        seen.add(period)
        passed = _number(row["passed"], f"Row {index}: passed", integral=True)
        failed = _number(row["failed"], f"Row {index}: failed", integral=True)
        if passed + failed == 0:
            raise ValueError(f"Row {index}: passed + failed must be greater than zero.")
        response = _number(row["response_ms"], f"Row {index}: response_ms", minimum=1e-9)
        cleaned.append(dict(period=period, passed=passed, failed=failed, response_ms=response))
    return cleaned


def load_csv(path):
    """Read strict batch CSV data with the same validation used by the web app."""
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)) or set(headers) != set(REQUIRED_COLUMNS):
            raise ValueError("CSV headers must be exactly: period,passed,failed,response_ms.")
        rows = []
        for index, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV line {index} has the wrong number of columns.")
            rows.append(row)
            if len(rows) > MAX_ROWS:
                raise ValueError(f"Use at most {MAX_ROWS:,} dataset rows online.")
    return validate_rows(rows)


def generate_demo(scale="micro"):
    """Generate fixed-seed teaching data with deliberate process changes."""
    if scale not in ("micro", "macro"):
        raise ValueError("Dataset scale must be micro or macro.")
    size = 30 if scale == "micro" else 10000
    rng = np.random.default_rng(DEMO_SEED)
    counts = rng.integers(60, 161, size) if scale == "micro" else rng.integers(80, 401, size)
    probabilities = np.full(size, .025)
    # These inserted signals demonstrate investigation; they do not prove defects.
    if scale == "micro":
        probabilities[20:24] = .16
    else:
        probabilities[6500:7200] = .075
    failed = rng.binomial(counts, probabilities)
    timing = np.maximum(50, rng.normal(280, 35, size))
    if scale == "micro":
        timing[20:24] += 270
    else:
        timing[6500:7200] += 290
    return [dict(period=f"batch-{i + 1:05d}", passed=int(counts[i] - failed[i]),
                 failed=int(failed[i]), response_ms=round(float(timing[i]), 2))
            for i in range(size)]


def wilson_interval(successes, total, confidence=.95):
    z = float(stats.norm.ppf((1 + confidence) / 2))
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return (0. if successes == 0 else max(0., center - half),
            1. if successes == total else min(1., center + half))


def _limits(p, counts):
    distance = 3 * np.sqrt(p * (1 - p) / counts)
    return np.maximum(0, p - distance), np.minimum(1, p + distance)


def _groups(rows, p, max_points=120):
    """Aggregate adjacent batches with count weighting, never average percentages."""
    step = max(1, math.ceil(len(rows) / max_points))
    output = []
    for start in range(0, len(rows), step):
        piece = rows[start:start + step]
        n = sum(row["passed"] + row["failed"] for row in piece)
        failed = sum(row["failed"] for row in piece)
        mean = sum(row["response_ms"] * (row["passed"] + row["failed"]) for row in piece) / n
        lo, hi = _limits(p, np.array([n]))
        rate = failed / n
        output.append(dict(first_period=piece[0]["period"], last_period=piece[-1]["period"],
                           first_row=start + 1, last_row=start + len(piece), batches=len(piece),
                           executions=n, failed=failed, failure_rate=rate, response_ms=mean,
                           LCL=float(lo[0]), CL=p, UCL=float(hi[0]),
                           control_signal=bool(rate < lo[0] or rate > hi[0])))
    return output


def _simulate(p, n, trials, seed):
    low, high = _limits(p, np.array([n]))
    lower, upper = float(low[0]), float(high[0])
    # Strict outside-limit events. CDF/SF avoid allocating arrays of n outcomes.
    below = math.ceil(lower * n) - 1
    above = math.floor(upper * n)
    exact = float(stats.binom.cdf(below, n, p) + stats.binom.sf(above, n, p))
    draws = np.random.default_rng(seed).binomial(n, p, trials)
    events = (draws / n < lower) | (draws / n > upper)
    observed = int(events.sum())
    lo, hi = wilson_interval(observed, trials, .99)
    return dict(representative_batch_size=n, fitted_failure_probability=p,
                LCL=lower, UCL=upper, exact_outside_probability=exact,
                simulated_outside_probability=observed / trials, outside_events=observed,
                trials=trials, seed=seed, ci99_low=lo, ci99_high=hi,
                exact_within_ci99=bool(lo <= exact <= hi),
                absolute_error=abs(observed / trials - exact),
                assumption="Independent Bernoulli test outcomes at the pooled fitted failure rate, with a fixed representative batch size. This validates the model's tail probability, not software quality.")


def _simulate_timing(times, counts, trials, seed):
    """Verify the weighted empirical expectation; not a population bootstrap CI."""
    probabilities = counts / counts.sum()
    target = float(np.average(times, weights=counts))
    rng = np.random.default_rng(np.random.SeedSequence([seed, 1]))
    draws = rng.choice(times, size=trials, replace=True, p=probabilities)
    # A constant empirical distribution has exactly zero Monte Carlo error.
    estimate = target if np.ptp(times) == 0 else float(draws.mean())
    se = 0. if np.ptp(times) == 0 else float(draws.std(ddof=1) / math.sqrt(trials))
    margin = float(stats.norm.ppf(.995)) * se
    low, high = estimate - margin, estimate + margin
    return dict(target_weighted_mean_ms=target, simulated_mean_ms=estimate,
                mean_standard_error_ms=se, mean_mc_ci99_low_ms=low,
                mean_mc_ci99_high_ms=high, target_within_mc_ci99=bool(low <= target <= high),
                absolute_error_ms=abs(estimate - target), trials=trials,
                assumption="Independent draws from the recorded batch means, selecting each batch with probability n_i / total executions. The interval measures Monte Carlo error around a fixed empirical expectation; it is not a population confidence interval or an individual latency model.")


def _image(figure):
    stream = BytesIO()
    figure.savefig(stream, format="png", dpi=135, bbox_inches="tight", facecolor="#ffffff")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def _plots(groups, rows, p, specification):
    x = np.arange(1, len(groups) + 1)
    color = "#bd3039"
    with PLOT_LOCK:
        process = Figure(figsize=(11.5, 4.5), constrained_layout=True)
        ax = process.subplots()
        rates = np.array([g["failure_rate"] for g in groups])
        flags = np.array([g["control_signal"] for g in groups])
        ax.plot(x, rates * 100, color="#30333b", linewidth=1.25, marker="o" if len(groups) <= 40 else None, markersize=3.5, label="Observed failed-test rate")
        ax.plot(x, [g["LCL"] * 100 for g in groups], color=color, linestyle="--", linewidth=1, label="Three-sigma control limits")
        ax.plot(x, [g["UCL"] * 100 for g in groups], color=color, linestyle="--", linewidth=1)
        ax.axhline(p * 100, color="#64748b", linewidth=1, label="Pooled center line")
        if flags.any():
            ax.scatter(x[flags], rates[flags] * 100, color=color, zorder=4, s=32, label="Outside-limit signal")
        ax.set(xlabel="Ordered batch" if len(groups) == len(rows) else "Consecutive batch group (count-weighted)", ylabel="Failed tests (%)", title="Failure-rate process chart")
        top=max(float(np.max(rates))*100,max(g['UCL'] for g in groups)*100)
        ax.set_ylim(0, min(100, max(1, top*1.15)))
        if p == 0:
            ax.text(.5,.5,'All recorded checks passed\nFitted center and control limits are 0%.\nSee the reported failure-rate interval.',
                    transform=ax.transAxes,ha='center',va='center',color='#606875',fontsize=10)
        ax.grid(axis="y", alpha=.18)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8, loc="upper left", ncol=2)
        process_url = _image(process)

        timing = Figure(figsize=(11.5, 4.6), constrained_layout=True)
        left, right = timing.subplots(1, 2, gridspec_kw={"width_ratios": [1.6, 1]})
        left.plot(x, [g["response_ms"] for g in groups], color="#30333b", linewidth=1.2)
        left.axhline(specification, color=color, linestyle="--", label=f"Batch-mean threshold: {specification:g} ms")
        left.set(xlabel="Ordered batch" if len(groups) == len(rows) else "Consecutive batch group", ylabel="Mean response time (ms)", title="Batch-mean timing")
        left.grid(axis="y", alpha=.18)
        left.legend(fontsize=8)
        values = [row["response_ms"] for row in rows]
        right.hist(values, bins=min(30, max(1, math.ceil(math.sqrt(len(values))))), color="#bd3039", alpha=.8, edgecolor="white")
        right.set(xlabel="Batch mean (ms)", ylabel="Number of batches", title="Distribution of batch means")
        for axis in (left, right):
            axis.spines[["top", "right"]].set_visible(False)
        return {"failure_chart": process_url, "timing_chart": _image(timing)}


def _format(value, digits=3):
    return f"{value:,.{digits}f}".rstrip("0").rstrip(".")


def _report(record, plots, message):
    summary = record["calculated"]
    simulation = record["simulation"]
    timing_simulation = simulation["timing_resampling"]
    scale = record["case"]["inputs"]["scale"]
    source = record["case"]["inputs"]["dataset_source"]
    source_label = {"demo": "Synthetic teaching data", "own": "User-supplied batch data",
                    "forevermart": "Recorded ForeverMart website checks"}[source]
    provenance = record.get("provenance", {})
    provenance_text = ""
    provenance_section = ""
    if source == "forevermart":
        provenance_text = '<p class="muted">Source: https://forevermart.vercel.app/ · '
        collected = provenance.get("captured_at_utc", provenance.get("collected_at_utc", provenance.get("capture_started_utc", "see dataset manifest")))
        provenance_text += f"Recorded: {escape(str(collected))}. HTTP measurements include client, network and hosting latency; they are not isolated server execution times. Stored checks are a dated sample, not a live monitor.</p>"
        scope_data = provenance.get("scales", {}).get(scale, {})
        provenance_fields = [
            ("Project URL", provenance.get("source_url", "https://forevermart.vercel.app/")),
            ("Collection started (UTC)", collected),
            ("Collection finished (UTC)", provenance.get("completed_at_utc", "See dataset manifest")),
            ("Collection method", provenance.get("method", "See dataset manifest")),
            ("Passing-check definition", provenance.get("check_definition", "See dataset manifest")),
            ("Timing definition", provenance.get("timing_definition", "Mean client-observed response time")),
            ("Project scope", provenance.get("scope_definition", "See dataset manifest")),
            ("Routes in this dataset", ", ".join(map(str, scope_data.get("routes", []))) or "See dataset manifest"),
            ("Raw check log", provenance.get("raw_log", "See dataset manifest")),
        ]
        provenance_table = "".join(f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>" for label, value in provenance_fields)
        limitations = "".join(f"<li>{escape(str(item))}</li>" for item in provenance.get("limitations", []))
        provenance_section = f'<section><h2>Recorded-data provenance</h2><table>{provenance_table}</table><ul>{limitations}</ul></section>'
    summary_rows = [
        ("Recorded batches", f"{summary['row_count']:,}"),
        ("Test executions", f"{summary['total_executions']:,}"),
        ("Passed / failed tests", f"{summary['total_passed']:,} / {summary['total_failed']:,}"),
        ("Pooled failed-test rate", _format(summary["failure_rate"] * 100) + "%"),
        ("95% Wilson interval", f"{_format(summary['failure_ci95_low'] * 100)}%–{_format(summary['failure_ci95_high'] * 100)}%"),
        ("Execution-weighted mean response", _format(summary["weighted_mean_response_ms"], 2) + " ms"),
        ("Median of batch means", _format(summary["median_batch_response_ms"], 2) + " ms"),
        ("95th percentile of batch means", _format(summary["p95_batch_response_ms"], 2) + " ms"),
        ("Batch-mean threshold", _format(summary["specification_ms"]) + " ms"),
        ("Batches above timing threshold", f"{summary['timing_threshold_batch_count']:,}"),
        ("Original batches outside p-chart limits", f"{summary['control_signal_batch_count']:,}"),
        ("Chart groups outside group limits", f"{summary['control_signal_group_count']:,} of {len(summary['chart_groups']):,}"),
    ]
    table = "".join(f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in summary_rows)
    sim_table = "".join(f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in [
        ("Representative batch size (rounded median)", f"{simulation['representative_batch_size']:,}"),
        ("Random trials", f"{simulation['trials']:,}"),
        ("Exact binomial outside-limit probability", f"{_format(simulation['exact_outside_probability'] * 100, 5)}%"),
        ("Monte Carlo outside-limit estimate", f"{_format(simulation['simulated_outside_probability'] * 100, 5)}%"),
        ("99% Wilson interval for simulation", f"{_format(simulation['ci99_low'] * 100, 5)}%–{_format(simulation['ci99_high'] * 100, 5)}%"),
        ("Absolute probability difference", _format(simulation["absolute_error"], 7)),
        ("Exact probability within simulated interval", "Yes" if simulation["exact_within_ci99"] else "No — an interval can miss by chance"),
    ])
    timing_table = "".join(f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in [
        ("Recorded execution-weighted mean", f"{_format(timing_simulation['target_weighted_mean_ms'], 4)} ms"),
        ("Simulated weighted empirical mean", f"{_format(timing_simulation['simulated_mean_ms'], 4)} ms"),
        ("Absolute mean difference", f"{_format(timing_simulation['absolute_error_ms'], 4)} ms"),
        ("99% interval for Monte Carlo mean error", f"{_format(timing_simulation['mean_mc_ci99_low_ms'], 4)}–{_format(timing_simulation['mean_mc_ci99_high_ms'], 4)} ms"),
        ("Recorded weighted mean within interval", "Yes" if timing_simulation["target_within_mc_ci99"] else "No — an interval can miss by chance"),
    ])
    boundary_note = ("<p class=\"notice\">No failures were recorded, so the fitted binomial model has p = 0 and its simulated outside-limit probability is zero. This conditional result does not show that the website can never fail; use the reported Wilson upper bound and gather broader test evidence.</p>" if summary["failure_rate"] == 0 else
                     "<p class=\"notice\">All checks failed, so the fitted binomial model has p = 1 and its control limits coincide at 100%. No outside-limit signal in this boundary case does not mean acceptable quality.</p>" if summary["failure_rate"] == 1 else "")
    sample_signals = summary["control_signal_periods"][:12]
    labels = ", ".join(escape(label) for label in sample_signals) or "No individual batch crossed the fitted limits."
    if len(summary["control_signal_periods"]) > 12:
        labels += f"; plus {len(summary['control_signal_periods']) - 12:,} further batches (see JSON export)."
    grouping = ("Every chart point represents one original batch." if len(summary["chart_groups"]) == summary["row_count"] else
                f"For readability, {summary['row_count']:,} original batches are pooled into {len(summary['chart_groups']):,} consecutive groups. Each group's failure rate is total failed / total executions, and its limits use that group's denominator. Grouping can reveal or hide signals; original-batch counts are reported separately.")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dataset quality analysis</title>
<style>:root{{--ink:#292c34;--red:#bd3039;--line:#dce0e5}}*{{box-sizing:border-box}}body{{margin:0;background:#f3f4f6;color:var(--ink);font:15px/1.6 Arial,sans-serif}}main{{max-width:1120px;margin:auto;padding:24px}}header{{background:var(--ink);color:white;padding:26px 30px;border-top:5px solid var(--red)}}h1{{font-size:29px;margin:4px 0 9px}}h2{{font-size:21px;margin:0 0 13px}}h3{{font-size:17px;margin:20px 0 8px}}header p{{margin:0;color:#e3e4e8}}.eyebrow{{text-transform:uppercase;font-size:12px;letter-spacing:1.4px;color:#f1bcc0}}section{{background:white;border:1px solid var(--line);padding:25px 30px;margin:18px 0}}.notice{{background:#fff7f7;border-left:4px solid var(--red)}}.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}}.kpi{{background:white;padding:20px;border:1px solid var(--line);border-top:3px solid var(--red)}}.kpi strong{{display:block;font-size:27px}}.muted{{color:#606875;font-size:13px}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-weight:600;width:60%}}tr:nth-child(even){{background:#f7f8fa}}img{{width:100%;height:auto;display:block}}code{{background:#f3f4f6;padding:3px 6px}}ul{{padding-left:21px}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}@media(max-width:700px){{main{{padding:12px}}section,header{{padding:18px}}.kpis,.two{{grid-template-columns:1fr}}h1{{font-size:24px}}}}</style></head><body><main>
<header><div class="eyebrow">Software Testing · Independent mini-project</div><h1>{'Micro' if scale == 'micro' else 'Macro'} dataset quality analysis</h1><p>{source_label} · Failure-rate control chart, timing analysis and simulation verification</p></header>
<section class="notice"><strong>{source_label}</strong><p>{escape(message)}</p>{provenance_text}</section>
<div class="kpis"><div class="kpi"><span>Test executions</span><strong>{summary['total_executions']:,}</strong></div><div class="kpi"><span>Failed-test rate</span><strong>{_format(summary['failure_rate'] * 100)}%</strong></div><div class="kpi"><span>Batch control signals</span><strong>{summary['control_signal_batch_count']:,}</strong></div></div>
<section><h2>Dataset summary</h2><table>{table}</table><p class="muted">A failed test execution is not necessarily a unique software defect. Repeated failures may have the same cause. Percentiles above describe batch means, not individual response times.</p></section>
{provenance_section}
<section><h2>Failure-rate process monitoring</h2><img src="{plots['failure_chart']}" alt="Observed failed-test rates, pooled center line and variable-denominator control limits"><p>{grouping}</p><p><strong>Original-batch signals:</strong> {labels}</p><p class="muted">Limits are fitted to this same dataset and are exploratory. An outside-limit signal prompts investigation; no signal does not prove control or acceptable quality. Low failure counts may require exact binomial limits instead of the approximate three-sigma chart.</p></section>
<section><h2>Response-time exploration</h2><img src="{plots['timing_chart']}" alt="Batch mean response times and histogram of original batch means"><p>The red threshold is your criterion for each batch's mean response time. Batches above it need review. This threshold is a requirement, separate from statistical control limits. No individual latency or SLA percentile claim is made from batch means.</p></section>
<section><h2>Simulation verification</h2><h3>1. Failure-count model</h3><p>Draw {simulation['trials']:,} independent synthetic batches of {simulation['representative_batch_size']:,} tests at the fitted failure probability. Compare the simulated fraction outside this batch's limits with the exact binomial tail probability.</p><table>{sim_table}</table>{boundary_note}<p class="muted">Seed: {simulation['seed']}. The 99% interval describes Monte Carlo sampling uncertainty, conditional on the fitted model; it excludes uncertainty in the fitted rate. Repeated tests may be correlated, and changing systems may violate this model.</p><h3>2. Response-time empirical resampling</h3><p>Draw {simulation['trials']:,} recorded batch means with replacement. Each batch is selected with probability equal to its execution count divided by total executions. The simulated average should approach the recorded execution-weighted mean.</p><table>{timing_table}</table><p class="muted">This interval measures random simulation error around the fixed recorded-data mean. It is not a population confidence interval or a bootstrap confidence interval, and these draws are batch means, not individual request latencies. More trials reduce simulation noise; they do not add real test evidence.</p></section>
<section><h2>Formulas and interpretation</h2><div class="two"><div><h3>Count-weighted calculations</h3><p><code>nᵢ = passedᵢ + failedᵢ</code><br><code>p̄ = Σfailedᵢ / Σnᵢ</code><br><code>pᵢ = failedᵢ / nᵢ</code></p><p><code>LCLᵢ = max(0, p̄ − 3√[p̄(1−p̄)/nᵢ])</code><br><code>UCLᵢ = min(1, p̄ + 3√[p̄(1−p̄)/nᵢ])</code></p><p><code>Weighted timing mean = Σ(nᵢ × mean_msᵢ) / Σnᵢ</code></p></div><div><h3>Practical QA follow-up</h3><ul><li>Investigate flagged batches using logs, test IDs, build versions and execution environment.</li><li>Separate product failures from flaky tests, unavailable services and invalid test data.</li><li>Record a defect with reproduction steps and a corrective action when a product issue is confirmed.</li><li>Retest the fix and compare later batches against a suitable stable baseline.</li></ul></div></div><p>The micro/macro labels describe analysis scale. Quality assurance is the wider prevention and process discipline; quality control measures outputs. They do not mean small data versus big data, and 10,000 rows alone do not constitute a Big Data architecture.</p></section>
<section><h2>Analysis assumptions</h2><ul><li>Rows are ordered batches as supplied; no dates or chronological order are inferred from labels.</li><li>Passed and failed are mutually exclusive exhaustive outcomes in each batch. All counts are retained.</li><li>Each response_ms value is that batch's mean measured on the same executions represented by its count.</li><li>Failure-rate intervals and binomial simulation assume independent comparable test outcomes. Mixed suites and correlated reruns can make that assumption unsuitable.</li><li>{'Demo values are generated with fixed seed 20260901, including deliberately inserted changes for teaching; they are not measured ForeverMart data.' if source == 'demo' else ('ForeverMart data come from the stored, dated HTTP check collection. An HTTP content or response check does not exercise all browser interactions, and repeated route checks may be correlated. HTTP success does not prove that the application is defect free.' if source == 'forevermart' else 'User-supplied values are analyzed as provided. Their origin, measurement procedure and truth have not been independently verified.')}</li></ul><p class="muted">Tools: Python · NumPy (aggregation, random generation) · SciPy (binomial probabilities, Wilson quantiles) · Matplotlib (charts). No textbook answer is available for an independent dataset.</p><p class="muted">Formula references: <a href="https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm" target="_blank" rel="noopener">NIST p-chart guidance</a> · <a href="https://asq.org/quality-resources/quality-assurance-vs-control" target="_blank" rel="noopener">ASQ quality assurance and quality control</a>.</p></section>
</main></body></html>"""


def evaluate_dataset(payload):
    """Calculate one micro/macro project and return an embeddable result page."""
    if not isinstance(payload, dict):
        raise ValueError("Please provide a dataset project object.")
    if payload.get("project_type", "dataset") != "dataset":
        raise ValueError("project_type must be dataset.")
    scale = payload.get("scale", "micro")
    if scale not in ("micro", "macro"):
        raise ValueError("Dataset scale must be micro or macro.")
    source = payload.get("dataset_source", "own" if "rows" in payload else "forevermart")
    if source not in ("forevermart", "demo", "own"):
        raise ValueError("Choose forevermart, demo or own as the dataset source.")
    if source != "own" and "rows" in payload:
        raise ValueError("Choose own dataset source to analyze supplied rows.")
    provenance = {}
    if source == "forevermart":
        filename = ROOT / "data" / f"forevermart_{scale}.csv"
        if not filename.is_file():
            raise ValueError(f"The recorded ForeverMart {scale} dataset is unavailable. Collect the website checks first or choose your own CSV data.")
        rows = load_csv(filename)
        manifest = ROOT / "data" / "forevermart_dataset_manifest.json"
        if manifest.is_file():
            provenance = json.loads(manifest.read_text(encoding="utf-8"))
    else:
        rows = validate_rows(generate_demo(scale) if source == "demo" else payload.get("rows"))
    specification = _number(payload.get("specification_ms", 500), "Response-time threshold", minimum=1e-9)
    trials = _number(payload.get("trials", 10000), "Simulation trials", integral=True, minimum=100, maximum=100000)
    seed = _number(payload.get("seed", DEMO_SEED), "Random seed", integral=True, maximum=2**32 - 1)
    n = np.array([row["passed"] + row["failed"] for row in rows], dtype=np.int64)
    failed = np.array([row["failed"] for row in rows], dtype=np.int64)
    times = np.array([row["response_ms"] for row in rows])
    total = int(n.sum())
    failed_total = int(failed.sum())
    p = failed_total / total
    low, high = _limits(p, n)
    rates = failed / n
    alerts = (rates < low) | (rates > high)
    ci_low, ci_high = wilson_interval(failed_total, total)
    weighted_mean = float(np.average(times, weights=n))
    groups = _groups(rows, p)
    summary = dict(row_count=len(rows), total_executions=total, total_passed=total - failed_total,
                   total_failed=failed_total, failure_rate=p, pass_rate=1 - p,
                   failure_ci95_low=ci_low, failure_ci95_high=ci_high,
                   weighted_mean_response_ms=weighted_mean,
                   weighted_std_batch_response_ms=float(np.sqrt(np.average((times - weighted_mean)**2, weights=n))),
                   median_batch_response_ms=float(np.median(times)), p95_batch_response_ms=float(np.quantile(times, .95)),
                   min_batch_response_ms=float(times.min()), max_batch_response_ms=float(times.max()),
                   specification_ms=specification, timing_threshold_batch_count=int(np.count_nonzero(times > specification)),
                   control_signal_batch_count=int(alerts.sum()),
                   control_signal_periods=[row["period"] for row, flag in zip(rows, alerts) if flag],
                   timing_threshold_periods=[row["period"] for row in rows if row["response_ms"] > specification],
                   control_signal_group_count=sum(g["control_signal"] for g in groups), chart_groups=groups,
                   first_batch_limits=dict(LCL=float(low[0]), CL=p, UCL=float(high[0])),
                   last_batch_limits=dict(LCL=float(low[-1]), CL=p, UCL=float(high[-1])))
    simulation = _simulate(p, max(1, int(math.floor(float(np.median(n)) + .5))), trials, seed)
    simulation["timing_resampling"] = _simulate_timing(times, n, trials, seed)
    if source == "demo":
        message = f"Independent synthetic {scale} dataset: {len(rows):,} teaching batches generated with fixed seed {DEMO_SEED}. These are not collected website measurements and are not stored textbook exercise data. No textbook answer comparison is performed."
    elif source == "forevermart":
        message = f"Independent ForeverMart {scale} dataset: {len(rows):,} recorded batches of website checks. These are measured project data, not stored textbook exercises. Failed checks do not necessarily represent unique software defects. No textbook answer comparison is performed."
    else:
        message = f"Independent user dataset: {len(rows):,} supplied batches. These values are not stored textbook exercise data. No textbook answer comparison is performed."
    record = dict(case=dict(id=f"{scale}-dataset", kind="dataset", title=f"{scale.title()} software-test dataset",
                            inputs=dict(scale=scale, dataset_source=source, specification_ms=specification,
                                        rows=rows)), calculated=summary, simulation=simulation,
                  comparisons=dict(book=dict(status="NOT_AVAILABLE", fields=[]), independent=dict(status="NOT_AVAILABLE", fields=[])),
                  case_seed=seed, provenance=provenance)
    plots = _plots(groups, rows, p, specification)
    return dict(category="independent", message=message, matched_exercises=[], record=record,
                report_html=_report(record, plots, message))
