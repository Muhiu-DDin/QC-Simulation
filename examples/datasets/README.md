# Independent batch dataset format

The application's **Recorded ForeverMart data** option uses actual dated HTTP checks in `data/forevermart_micro.csv` and `data/forevermart_macro.csv`. Their measurement details and collection limitations belong in `data/forevermart_dataset_manifest.json`. These files are separate from the textbook exercise inputs and answers.

To analyze your own measurements, upload a CSV with exactly these headers:

```csv
period,passed,failed,response_ms
batch-01,98,2,280.5
batch-02,118,2,296.7
```

`own_dataset_template.csv` contains **illustrative synthetic example values**. Replace them with your measured data; these example rows are not ForeverMart observations.

| Column | Meaning |
| --- | --- |
| `period` | A unique batch label; CSV row order determines chart order. |
| `passed` | Nonnegative whole number of passing checks in that batch. |
| `failed` | Nonnegative whole number of failing checks in that batch. |
| `response_ms` | Positive finite mean response time in milliseconds for the same checks counted in that row. |

Each batch must contain at least one check. The online analyzer accepts at most 20,000 rows, subject to its request-size limit. Failed checks are outcomes, not necessarily distinct software defects.

The analyzer pools failure counts across all executions rather than averaging percentages. Response-time means are also weighted by execution counts. It reports approximate variable-denominator p-chart signals and two simulations: a fitted binomial failure model, and resampling of recorded batch means with count weights. Simulated uncertainty describes Monte Carlo error; it does not validate the real-world measurement process.

If you want additional optional **synthetic teaching data**, run from the project folder:

```powershell
.\.venv\Scripts\python.exe examples\datasets\generate_demo.py
```

This writes `synthetic_micro.csv` (30 rows) and `synthetic_macro.csv` (10,000 rows) with fixed seed `20260901`. They include deliberately inserted process changes for chart demonstrations. They are not collected website data, and their row counts do not establish a Big Data system. No textbook comparison is performed for any independent dataset.
