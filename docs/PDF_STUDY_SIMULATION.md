# ForeverMart PDF study and simulation

The default micro/macro source is the original study behind the attached `report.pdf`, captured on **7 October 2026, Pakistan time**. The website now recalculates that study, compares its results with separately retained answers, and adds simulation. It does not collect fresh measurements when you press **Analyse and simulate**.

| Study | Recorded data | Calculations and recorded-data charts | Simulation |
|---|---|---|---|
| Micro | 25 groups × 5 catalog API timings = 125 requests | Individual latency summaries; mean/range charts; histogram and sequence; catalog exploration | Pick 25 whole recorded groups with replacement for each trial. Recalculate the study mean and chart limits. |
| Macro | 20 rounds × the same 5 service checks = 100 checks | Service pass/fail counts; p chart; endpoint median/P95 and boxplot; catalog exploration; separate browser findings | Pick 20 whole rounds with replacement for each trial to explore timing means. Separately compare the binomial failure-count formula with Monte Carlo estimates. |

The five macro services are storefront HTML, deployed JavaScript, catalog API, one product detail API, and anonymous access rejection. **HTTP 401 is a pass for the last check**, because an unauthenticated request should be refused.

The recorded study has **zero failures in these 100 service checks**. Its fitted binomial failure rate is therefore zero; this simulation also produces zero failures. That boundary result does not establish zero future risk. The recorded response times still vary, so resampling whole rounds gives a useful illustration of timing sensitivity. The pooled failure interval assumes independent, comparable outcomes; the different purposes and possible correlation of these checks limit that interpretation.

There are also **15 separate browser checks: 13 passed and two issues against the study's usability criteria**. Their original observations, cart screenshots, remedies and retest steps appear in the macro report. They are never mixed into the 100 service checks. No new browser testing or defect discovery occurs during simulation.

## Reading the results

- **Recorded data** sections and charts reproduce measurements from the original study.
- **PDF study comparison** recalculates the full-precision answers and compares them with `analysis.json`, retained from the original study. The PDF displays rounded values.
- **Simulation output** plots show averages of randomly resampled studies. These are calculations using existing observations, not additional ForeverMart requests.
- The **exploratory 95% bootstrap interval** shows sensitivity to which whole groups are selected, assuming groups are independent and comparable.
- The separate **99% Monte Carlo mean interval** measures simulation noise around the empirical mean. More trials reduce this noise; they do not increase real coverage or remove bias in the original measurements.
- A fixed **seed** reproduces the same random draws. Changing it changes simulation results while recorded calculations remain unchanged.

The micro study has mean-chart signals at groups **13 and 14**, and range-chart signals at groups **1, 3, 12 and 13**. Investigate this changing variability and possible serial correlation before treating the baseline as stable. Bootstrap intervals are illustrative sensitivity analysis here, not a guaranteed population performance statement. Control limits and statistical outliers do not automatically identify product defects.

## Inputs, formulas and source integrity

Original source files live in `data/forevermart_study/`. `requests.csv` contains all 225 full-precision measurements; metadata describes the protocol. The product snapshot and separate UI evidence are preserved. The original `analysis.json` and `validation.json` are frozen references. Source SHA-256 checks detect changed evidence; a reference mismatch is displayed instead of being silently replaced.

Micro calculations use five observations per group:

```text
group mean = sum(t1...t5) / 5
group range = max(t1...t5) - min(t1...t5)
grand mean = mean(group means)
average range = mean(group ranges)
Xbar limits = grand mean +/- 3 * average range / (2.326 * sqrt(5))
R limits = 0, 2.114 * average range
```

These are the n=5 factors used in the original PDF and Levin/Rubin's *Statistics for Management*, Chapter 10 and Appendix Table 9. In particular, retain **D4 = 2.114** rather than substituting a differently rounded constant. Percentiles use NumPy linear interpolation; sample standard deviation uses n−1.

Macro calculations use the recorded failure proportion and a fixed round size of five:

```text
pbar = total failed / total checks
p-chart limits = pbar +/- 3 * sqrt(pbar * (1-pbar) / 5), clipped to [0,1]
```

The timing target is **optional and initially empty**. The original PDF has no stated SLA. If you add a target, the study report counts individual recorded request timings above it; this is your additional requirement, separate from chart limits. Aggregate CSV reports instead evaluate batch means because individual timings are unavailable.

## Your own data

For the same micro mean/range analysis, import:

```csv
period,t1_ms,t2_ms,t3_ms,t4_ms,t5_ms
Group 1,650,670,660,680,655
Group 2,660,655,675,665,650
Group 3,670,690,680,665,660
Group 4,655,660,670,650,675
Group 5,665,675,660,680,655
```

These are illustrative values. Supply 5–500 uniquely labelled groups; every timing must be finite, positive, and measured from a successful request. Failed attempts need a separate outcome record; do not replace them with invented timings. Your uploaded data have no stored PDF or textbook answer, and the report says so.

For existing aggregate pass/fail analysis, either scale still accepts `period,passed,failed,response_ms` (up to 20,000 rows and 2 MB). `response_ms` is that batch's mean on the executions represented by its counts. These data support failure-rate charts and weighted mean/model verification. **An average alone cannot reconstruct individual P95/P99, within-group ranges, or service-specific performance.** Those extra results require raw observations and service labels.

The earlier 11 October homepage/route HTTP sample is retained in the existing `data/forevermart_micro.csv`, `forevermart_macro.csv` and manifest for provenance and API compatibility (`dataset_source: forevermart`). It is distinct from the PDF study and is no longer the default UI or CLI source. The synthetic demo is separately labelled example data.

## Export and submission

Choose **Micro and macro datasets**, select **ForeverMart — attached PDF study**, choose Micro or Macro and press **Analyse and simulate**. Use **Download report** for a standalone HTML report with charts and original evidence. Open it in your browser and use Print → Save as PDF for submission; open the recorded-input details first if you want the full input tables printed. **Download result JSON** preserves calculated values, simulation settings and provenance.

The CLI produces equivalent reports:

```powershell
.\.venv\Scripts\python.exe run.py --project micro --trials 10000
.\.venv\Scripts\python.exe run.py --project macro --trials 10000
```

The original PDF is a reference study. The website report adds the simulation evidence requested for the micro/macro assignment. Submit that combined measurement-and-simulation report, identifying the study date and assumptions. It remains separate from Part 2B's exercise verification and Part 3's defect report.

Method references: [NIST mean/range chart guidance](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm), [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html). Tools: Python, NumPy, SciPy, Matplotlib; the browser renders the results and exports reports.
