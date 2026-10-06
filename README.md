# Software Testing - Chapter 10 QC Simulation

A working Python project for **Portfolio Part 2B** of Software Quality Engineering and Testing. It verifies the numerical exercises in the supplied *Statistics for Management*, Chapter 10, **Quality and Quality Control** (printed pp. 465-515; PDF pp. 480-530).

The project contains **92 numerical cases**, covering all nine self-check exercises and every regular Chapter 10 exercise with supplied numerical data, including subparts and reused datasets. Conceptual exercises and problems without observations are addressed in [the chapter guide](docs/CHAPTER10_GUIDE.md). Worked examples in the explanatory text are reference material; they are not additional exercise cases. Parts 1, 2A, 2C and 3 are outside this project.

## Start here on Windows

Open PowerShell in `SoftwareTesting-Simulation`:

```powershell
# Only needed on a fresh installation:
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Calculate every exercise, compare answers, simulate, and produce graphs:
.\.venv\Scripts\python.exe run.py --strict

# Run mathematical and regression checks:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If `py -3` cannot find Python, use `python -m venv .venv` or the full path to your installed Python. Python 3.11 or newer is recommended. The environment in this workspace has already been created and the project has been run. No environment activation is required. `requirements-lock.txt` records the exact packages used for verification; install it instead of `requirements.txt` to reproduce this environment (including optional PDF inspection packages).

On macOS/Linux, substitute `.venv/bin/python` for `.\.venv\Scripts\python.exe` and create the environment with `python3 -m venv .venv`.

After running, open **[output/report.html](output/report.html)** in a browser. It contains every case, its source page, reference comparisons, interpretation, graph, original inputs and simulation evidence. Also generated:

The report presents textbook comparisons and independent validation separately, with readable rounded values. Expand **Input values** or **Simulation verification** for supporting details. Full precision, seeds, dependency versions and file hashes remain in `results.json`.

| Output | Purpose |
|---|---|
| `output/comparison.csv` | Field-by-field calculated/reference differences and tolerances |
| `output/results.json` | Complete inputs, calculations, simulation intervals, seed and dependency versions |
| `output/graphs/*.png` | Separate exportable charts for each numerical case |

You can also double-click `run_project.cmd` after dependencies are installed.

## Your proposed answer-comparison design

Your idea is sound. Inputs, reference answers and the calculation engine must be separate so an incorrect calculation cannot generate its own supposed correct answer.

| File | Role |
|---|---|
| `data/chapter10_inputs.json` | Transcribed inputs, exercise IDs, page numbers and interpretations |
| `data/chapter10_answers.json` | Frozen reference answers, source labels and tolerances |
| `book_answers.py` | Loads stored answers without performing calculations |
| `qc/calculations.py` | NumPy/SciPy calculations and input validation |
| `qc/simulation.py` | Reproducible Monte Carlo experiments |
| `qc/comparison.py` | Compares calculated fields against stored references |
| `qc/reporting.py` | Matplotlib graphs and HTML/CSV/JSON reports |
| `run.py` | Command-line entry point |

There are three reference types:

1. **`printed_book`**: the 24 cases with printed self-check answers. The original misprint in SC10-5(b) is retained and flagged.
2. **`approximate_graph_reading`**: 12 visually estimated OC-graph answers, with a tolerance of 0.02 in probability.
3. **`independently_solved`**: all 92 cases have a baseline calculated separately using `math` formulas, then saved before runtime verification. These are our solutions, **not book answer-key entries**. The supplied book does not print answers for the other regular exercises.

The independent reference checks implementation consistency; it is not an independent mathematical proof of the formulas. Printed solutions, source checks and mathematical tests provide additional evidence. Missing printed answers remain visibly marked `NO_BOOK_ANSWER`.

Numerical matches use **absolute tolerances** appropriate to printed rounding, not exact floating-point equality. SC10-5(b) has status `SOURCE_ERRATUM`, with the raw `9` reference shown beside calculated `0.9`. Known source errors are not treated as unexplained calculation failures by `--strict`.

## Select exercises or change the simulation

```powershell
.\.venv\Scripts\python.exe run.py --list
.\.venv\Scripts\python.exe run.py --case SC10-1
.\.venv\Scripts\python.exe run.py --case 10-14 --case 10-14c --case 10-20 --case 10-20c
.\.venv\Scripts\python.exe run.py --case 10-38 --trials 500000 --seed 42 --output output\oc-study
```

`--case` accepts an exact ID or, if no exact ID exists, an exercise prefix covering its lettered subparts. The default is 100,000 trials and seed 20260901. Each ID receives a stable derived seed, so selecting one case produces the same simulation as that case in a complete run.

Exit codes: `0` successful run; `1` reference mismatch with `--strict`; `2` invalid input or missing files. Random Monte Carlo interval misses are reported, but do not set exit code 1.

## Enter your own data

Copy [examples/custom_inputs.json](examples/custom_inputs.json), replace its measurements, and run:

```powershell
.\.venv\Scripts\python.exe run.py --input examples\custom_inputs.json --output output\custom
```

The examples illustrate software response times, failed test outcomes and acceptance sampling; their data are synthetic. You may provide a single case object or `{ "cases": [...] }`. Each case needs `id`, `title`, `kind` and `inputs`. Use unique IDs containing only letters, digits, hyphens and underscores.

| `kind` | Required inputs |
|---|---|
| `xbar` | `n` and either `observations` (rows of n measurements), `means` + `ranges`, `mean` + `rbar`, or `mean` + `se` |
| `range` | `n` and raw rows, `means` + `ranges`, or `rbar` |
| `p` | `n` and `counts` or `proportions`; optional `p` sets the target center, otherwise estimate it |
| `acceptance` | `N`, `n`, `c`, `p`, `risk` (`producer`/`consumer`), `model` (`binomial`/`poisson`) |
| `proportion_test` | `n`, `successes`, `p0`; optional `alpha` (default .05) |
| `pareto` | `counts`: mapping from category names to nonnegative integer counts |
| `range_identity` | Positive `lcl` and `rbar` for Exercise 10-17(e) |

Proportions must be fractions such as `0.025`, not percentages such as `2.5`. All subgroups in a case must have the same size. The supplied factor table supports n=2..25 for range-based mean/range charts; known-standard-error mean charts are not limited to that table.

If custom data reuse an existing exercise ID but change its inputs, the default book/reference comparisons are disabled. To compare custom data against your teacher's answers, provide a separate answer JSON with the same structure and pass `--answers path\to\answers.json`. The report retains the SHA-256 of the input and reference files for traceability.

## What the simulations actually verify

The analytical answers are deterministic. Monte Carlo introduces repeated random samples to check the **sampling model**:

- Acceptance sampling estimates the chance of rejecting a good lot or accepting a bad lot. A 99% Wilson interval accompanies each probability estimate.
- Mean charts use a fitted normal distribution of subgroup means and check the three-standard-error tail probability.
- Proportion charts simulate Bernoulli outcomes and compare limit violations with the **exact discrete binomial tail**, which need not equal the normal 0.27% tail.
- Range charts simulate independent normal subgroups and verify the expected range against the fitted Rbar. The range distribution is not assumed normal.
- Aggregate proportion tests simulate the exact binomial null tail; the normal z-test is reported separately.
- Pareto counts and the range-identity exercise require arithmetic and plotting; random simulation is not appropriate.

An interval can miss the theoretical value by chance, especially across many cases. Increase trials to reduce sampling error; do not choose seeds just to force a match. Control-chart simulation assumes fixed fitted parameters and is not a bootstrap confidence interval for estimated control limits.

## Portfolio use

Use the HTML report and PNG charts with your handwritten Part 2A. For each selected problem, explain the inputs, formula, printed/independent answer, calculated result, difference/tolerance, Monte Carlo model and interval, chart interpretation, and corrective action. Read [SOURCE_NOTES](docs/SOURCE_NOTES.md) before reporting source discrepancies and [CHAPTER10_GUIDE](docs/CHAPTER10_GUIDE.md) for complete exercise coverage.

The assignment specifies 28 September 2026 for Parts 1 and 2A and allows additional time for Part 2B; it supplies no later fixed Part 2B deadline. This project does not invent one. Instructor approval of final portfolio formatting and scope remains necessary.

## Maintenance

The normal run never creates or edits reference answers. `tools/build_catalog.py` and `tools/build_references.py` are authoring tools: run them **only after intentional source/data changes**, then review their JSON changes and rerun checks. They are provided so the transcriptions and independent baseline method are inspectable.

After a report layout change, `tools/refresh_reports.py` updates existing reports from saved `results.json` files without repeating calculations or simulations.

Optional book inspection: install `pymupdf` and run `tools/inspect_book.py <path-to-pdf> --pages 480-530` or `--render 507`. The source book is never modified or copied into the project. Extracted scratch text/images go into ignored `tmp/pdfs`.

## Publish reports on Vercel

`tools/prepare_vercel.py` creates an isolated `vercel-site/` folder containing the calculator homepage, the saved book report as `book-results.html`, the Python endpoint, all referenced charts, and CSV/JSON exports. It excludes custom reports, the source PDF, and the local Python environment.

```powershell
.\.venv\Scripts\python.exe tools\prepare_vercel.py
npx.cmd --yes vercel@latest login
npx.cmd --yes vercel@latest --cwd vercel-site --prod
```

The deployment includes the book report, an input form, and a Python calculation endpoint. After recalculating or updating the application, run the preparation script again before redeploying.

## Calculate using the input form

Open [the online calculator](https://vercel-site-tawny-omega.vercel.app/calculator.html).

1. Select the calculation type.
2. Choose **Compare with a book question**, then select the question from the book dropdown. Alternatively, choose **My own data (not in the book)** to disable that dropdown.
3. Enter the numerical values in the blank fields. Each placeholder explains what to enter.
4. Press **Enter** in a numerical field or click **Calculate and compare** to show one result.

In book mode, the question automatically determines the input method; **Available data** is hidden. For example, SC10-1a shows subgroup size, grand mean, and average range. Alternative input methods remain available in own-data mode.

Book mode calculates from your submitted values and compares with the selected exercise's available textbook and independent reference answers. If your values differ from the selected question, a message explains that answer differences are expected. Own-data mode always displays an **Independent data** message and disables reference comparisons, even if the entered values happen to match a book question. Results appear only after submission. The website starts with this calculator; the full saved report remains available under **Book results**.

For a local version, prepare the application and start the server:

```powershell
.\.venv\Scripts\python.exe tools\prepare_vercel.py
.\.venv\Scripts\python.exe serve.py
```

Keep that terminal open and visit `http://127.0.0.1:8000/calculator.html`. Opening the calculator HTML directly as a file will not run the Python endpoint.

The `web/` folder contains the form, styling, and browser code. `qc/web_service.py` connects submitted inputs to the existing calculation, simulation, comparison, and report functions. `api/calculate.py` exposes that service on Vercel; `serve.py` provides it locally. Reference answer files remain unchanged by form submissions.
