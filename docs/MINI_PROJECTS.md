# ForeverMart micro and macro mini-projects

The assignment's Part 2B verifies numerical answers using software. Part 2C asks for data, formulas, graphs and exploratory analysis at micro and macro levels. This project offers both through separate forms and reports.

## Dataset source and collection

The default datasets use actual HTTPS observations from [ForeverMart](https://forevermart.vercel.app/). Micro covers 60 homepage checks in 20 batches. Macro covers 300 checks in 100 batches across the homepage, collection, about, contact, cart, login, orders and place-order routes. Measurements were collected sequentially on 11 October 2026, with three requests per batch and a short delay between requests.

The raw evidence is `data/forevermart_http_checks.json`. Each entry records the URL, UTC timestamp, HTTP status, response content type, byte count, elapsed milliseconds and passing-check outcome. Aggregate CSV rows retain the number passed, number failed and arithmetic mean elapsed time. `data/forevermart_dataset_manifest.json` identifies the measurement definitions, limitations and SHA-256 hashes. It makes the input-to-result path inspectable.

A passing check means HTTP 200 + HTML + the React root element. It tests delivery of the app document shell. It does not execute browser JavaScript or test product search, authentication, payment, cart updates or ordering. No accounts, payments or orders were created by this collection.

All 360 recorded checks passed that criterion. Their response times varied. Elapsed timing includes the client's connection, TLS negotiation, network transit and response download; it is not browser rendering time or an isolated backend execution measurement.

Micro and macro are relative analysis scopes here. The 100-row macro sample is not industrial Big Data. Up to 20,000 batch rows can be imported for larger collected datasets. Optional synthetic examples demonstrate that larger path but are not substituted for website measurements.

## Calculations

For batch i, n_i = passed_i + failed_i. The pooled failure rate is p-bar = sum(failed_i) / sum(n_i). It is not the unweighted average of batch percentages when their sizes differ.

The exploratory p-chart limits for each batch are:

```
LCL_i = max(0, p-bar - 3 * sqrt(p-bar * (1-p-bar) / n_i))
CL_i  = p-bar
UCL_i = min(1, p-bar + 3 * sqrt(p-bar * (1-p-bar) / n_i))
```

These follow the [NIST proportion-chart model](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm), substituting each batch's denominator. Limits are fitted using the observed sample and are exploratory. Correlated checks or mixed routes may violate the independent-binomial assumption. For rare failures or small denominators, the three-sigma normal approximation is coarse; the simulation comparison uses the exact binomial tail for the stated limits.

The 95% Wilson interval estimates uncertainty in the overall recorded failure proportion under independent comparable outcomes. With zero failures, its upper bound remains positive. A zero fitted rate makes the conditional binomial simulation degenerate; that does not prove the website cannot fail.

The weighted response mean is sum(n_i * response_ms_i) / sum(n_i). Median and 95th-percentile summaries describe **batch means**. Individual-request percentiles cannot be reconstructed from aggregate batch means; the raw log must be used for that separate calculation.

## Simulation verification

Two comparisons are shown:

1. **Failure-count model:** draw repeated binomial counts for a representative batch size at the fitted pooled rate. Compare the observed outside-limit proportion with the exact binomial CDF/SF calculation. Report the difference and a 99% Wilson Monte Carlo interval.
2. **Timing resampling:** select recorded batch means with replacement, with selection probability n_i / total executions. Compare the average of the simulated draws with the calculated execution-weighted mean. Its 99% interval describes Monte Carlo error around this fixed empirical expectation. It is not a population confidence interval or a bootstrap interval.

Simulation trials are random draws from these models. Increasing trials reduces numerical simulation noise; it does not increase the number of real website measurements or repair defects. A confidence interval can miss its target by chance, so the program does not select a seed merely to make comparisons pass.

## Graphs and interpretation

The failure chart shows fitted limits and observed batch rates. For more than 120 rows, it pools adjacent batches into at most 120 groups using total failures / total checks, retaining all original batch alerts in JSON. Grouping can hide or reveal signals, so original and grouped counts are reported separately.

The timing graph shows ordered batch means and an editable target. The histogram shows the distribution of original batch means. The default 500 ms threshold is an assignment study criterion; no ForeverMart SLA was supplied. A threshold exceedance is a signal to review the measured performance, not automatically a confirmed product defect.

## Practical QA workflow

```
Define test and criterion -> Record actual checks -> Validate data
-> Calculate and plot -> Simulate the stated model -> Investigate signals
-> Document a confirmed defect and remedy -> Retest -> Collect later evidence
```

Keep a failing check's timestamp, URL, environment and logs. Distinguish a product failure from a network problem, test-data issue or flaky test. Confirm the defect through reproduction before adding it to Part 3. Failed checks may repeat the same defect and must not be counted as unique bugs.

[ASQ](https://asq.org/quality-resources/quality-assurance-vs-control) distinguishes confidence-building quality assurance activities from output-focused quality control. Neither term is defined by dataset size. The existing 70-defect Part 3 report is separate and has not been changed by this update.

## Own data

Use exactly `period,passed,failed,response_ms` in the CSV header. Counts must be nonnegative whole numbers, their sum positive, labels unique and response means finite and positive. Keep rows in the intended analysis order. Quoted labels containing commas are supported. The upload limit is 20,000 rows and 2 MB.

Imported data always show an independent-data notice and have no textbook answer comparison. Choose either micro or macro to label the intended scope; the program reports the actual row count regardless of the chosen label.
