# Software Testing — QC Simulation and ForeverMart Mini-projects

This Python project covers **Part 2B numerical verification** and **Part 2C micro/macro data projects** for Software Quality Engineering and Testing. The book scope is now **exercises 10.40–10.59 only**.

The supplied assignment places software verification of numerical answers in Part 2B and micro/macro mini-projects in Part 2C. Both are available in this application. QA and QC describe quality activities; they are not definitions of small and large data ([ASQ explanation](https://asq.org/quality-resources/quality-assurance-vs-control)).

## Open the application

Your existing `.venv` has the required NumPy, SciPy and Matplotlib packages. From PowerShell in this project folder, run these commands one at a time:

```powershell
.\.venv\Scripts\python.exe tools\prepare_vercel.py
.\.venv\Scripts\python.exe serve.py
```

Open **http://127.0.0.1:8000/calculator.html**. Keep the terminal open; **Ctrl+C** stops the server. You can also run **`run_ui.cmd`** from Windows File Explorer, or type `.\run_ui.cmd` in PowerShell. Clicking its filename in the VS Code Explorer opens its source code.

If an older server is still running, stop it with Ctrl+C and restart after preparing the update. To use another port, run `serve.py --port 8001` and open `http://127.0.0.1:8001/calculator.html`.

This is a Python application. `npm run dev` is not its launch command. No environment activation or PowerShell execution-policy change is needed for the commands above.

Only for a fresh installation:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Part 2B — book numericals

1. Select **Book numericals · Part 2B**.
2. Choose the calculation type and **Compare with a book question**.
3. Select a question. Only that question's required fields appear.
4. Enter its values manually, or use **Load book values** and edit them.
5. Press **Enter** or **Calculate and compare**. One result appears with calculations, a chart and available reference comparisons.

Choose **My own data** to use independent numerical inputs; the book question dropdown is disabled and no book comparison is made. If you select a book question and enter different values, the result explains that differences from its stored answer are expected.

There are **22 calculation cases across 11 numerical exercises** in the requested range. Lettered subparts account for the extra cases. The other **9 questions** are conceptual or provide no numerical observations; they are explained in [the assigned exercise guide](docs/ASSIGNED_EXERCISES.md). The application does not manufacture numbers for them.

| Exercises | Calculation |
|---|---|
| 10.40(a), 10.40(b) | One-sided proportion test; weekly p chart |
| 10.44, 10.45 | Mean and range charts for the supplied hourly data |
| 10.46 | Pareto chart of subcontractor faults |
| 10.47(a–d), 10.48(a–d) | Acceptance-sampling risks |
| 10.50, 10.51 | Mean and range charts for the supplied disk-coating data |
| 10.52 | Proportion chart for the supplied photographic-print quality data |
| 10.55(a–c), 10.56(a–c) | OC-graph comparisons and acceptance probabilities |

The supplied PDF does **not** contain published answer-key entries for these regular exercises. All 22 cases have separately solved, frozen references; the six subparts of 10.55/10.56 also have approximate readings of the printed OC graph. The report distinguishes these sources and uses rounding tolerances. “Independent validation” does not mean “publisher answer.”

Useful commands:

```powershell
# List only the assigned cases:
.\.venv\Scripts\python.exe run.py --list

# Generate the assigned numerical report:
.\.venv\Scripts\python.exe run.py --strict

# Run one exercise, including its lettered numerical subparts:
.\.venv\Scripts\python.exe run.py --case 10-40 --output output\question-40
```

The default report is `output/report.html`; `comparison.csv`, `results.json` and `graphs/` provide exportable evidence. Outside-range book IDs are excluded from the default run and book dropdown.

## Part 2C — ForeverMart PDF study and simulation

The default website and CLI now reproduce the original study behind your attached **report.pdf**, captured on **7 October 2026 (Pakistan time)**. Calculations are compared with that study's separately frozen answers. Simulation is added to the recorded-data analysis; pressing the button does not collect new website measurements.

| Study | Scope | Groups / rounds | Actual recorded requests |
|---|---|---:|---:|
| Micro | Product catalog API timings | 25 × 5 timings | 125 |
| Macro | Same five service checks in every round | 20 × 5 checks | 100 |

Micro produces individual latency summaries, mean/range charts, timing exploration and catalog statistics. Macro produces service pass/fail results, a p chart, endpoint performance, catalog exploration and **15 separate browser checks (13 passed, two study-criterion issues)** with original cart evidence, remedies and retest steps. Those browser issues are not added to the 100 service checks. Expected HTTP 401 counts as a pass for anonymous access protection.

Each simulation randomly picks whole recorded groups with replacement, then recalculates the study average. Micro also recalculates chart limits. Macro separately checks the binomial failure-count formula. The reports distinguish **recorded-data charts** from the **simulation distribution chart** and explain the exploratory bootstrap interval separately from Monte Carlo error. Fixed data, trials and seed reproduce the results. The original study is a dated sample, not a live monitor or load test.

1. Open **Micro and macro datasets · Part 2C**.
2. Choose **ForeverMart — attached PDF study** and Micro or Macro.
3. Leave the timing target empty unless you have an additional requirement.
4. Select **Analyse and simulate**.
5. Use **Download report** for the standalone HTML report; open it and Print → Save as PDF if needed. Use **Download result JSON** for calculated values and provenance.

The chart signals and bootstrap intervals need careful interpretation because the observations are serial and the micro baseline has changing variability. They do not prove a software defect, a stable process or an SLA. [The PDF-study guide](docs/PDF_STUDY_SIMULATION.md) explains the data, formulas, assumptions, simulation and submission.

```powershell
.\.venv\Scripts\python.exe run.py --project micro --trials 10000
.\.venv\Scripts\python.exe run.py --project macro --trials 10000
```

These generate `output/forevermart-micro/report.html` and `output/forevermart-macro/report.html` with charts and JSON. The earlier 11 October homepage/route sample remains preserved for traceability; it is distinct from the PDF study. The synthetic demo is explicitly labelled example data.

## Use your own dataset

For equivalent micro mean/range charts, import **five individual successful timings per group**, with 5–500 uniquely labelled groups:

```csv
period,t1_ms,t2_ms,t3_ms,t4_ms,t5_ms
Group 1,650,670,660,680,655
Group 2,660,655,675,665,650
Group 3,670,690,680,665,660
Group 4,655,660,670,650,675
Group 5,665,675,660,680,655
```

For aggregate pass/fail analysis in either scale, the existing format still works (maximum 20,000 rows and 2 MB):

```csv
period,passed,failed,response_ms
batch-001,98,2,240.5
batch-002,95,5,310.8
```

These examples are illustrative. `response_ms` is the positive mean for the same executions represented by the nonnegative whole pass/fail counts. Aggregate means cannot reconstruct individual latency percentiles or within-group ranges. Own-data results never claim a match with textbook or original PDF answers. The form provides downloadable templates.

```powershell
.\.venv\Scripts\python.exe run.py --project macro --dataset my_data.csv --threshold-ms 700 --output output\my-dataset
```

Custom numerical exercises still use the existing JSON format:

```powershell
.\.venv\Scripts\python.exe run.py --input examples\custom_inputs.json --output output\custom
```

## Files and responsibilities

| Location | Purpose |
|---|---|
| `data/chapter10_inputs.json` | Preserved full source transcription; runtime assignment filter selects 10.40–10.59 |
| `data/chapter10_answers.json`, `book_answers.py` | Preserved frozen answers and their provenance; never generated from runtime results |
| `data/assignment_scope.json`, `qc/scope.py` | Active exercise range and numerical/conceptual coverage |
| `data/forevermart_study/`, `data/forevermart_study_manifest.json` | Original PDF study measurements, frozen answers, catalog and UI evidence |
| `data/forevermart_micro.csv`, `data/forevermart_macro.csv` | Preserved earlier 11 October HTTP sample, distinct from the PDF study |
| `data/forevermart_http_checks.json` | Raw evidence for every recorded request |
| `data/forevermart_dataset_manifest.json` | Collection dates, routes, definitions and file hashes |
| `qc/calculations.py`, `qc/simulation.py`, `qc/comparison.py` | Numerical formulas, sampling models and reference comparisons |
| `qc/dataset_projects.py` | Aggregate CSV analysis and dataset dispatch |
| `qc/study_data.py`, `qc/study_projects.py` | Original PDF-study recalculation, raw micro analysis, bootstrap simulation and report |
| `qc/web_service.py`, `api/calculate.py`, `serve.py` | Shared calculation service, web endpoint and local server |
| `web/` | Input forms, browser code and the charcoal/red theme |
| `tools/prepare_vercel.py`, `vercel-site/` | Prepared website; only the 22 assigned book cases and references are exported |
| `output/` | Generated reports and charts; existing Part 3 report files are preserved |
| `tests/` | Mathematical, validation, scope and service checks |

`run_project.cmd` generates and opens the static **book report**. `run_ui.cmd` starts the **interactive application**.

## Verification and maintenance

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The legacy collector can refresh the separate 11 October-style HTTP sample; it does not alter or replace the frozen PDF-study evidence:

```powershell
.\.venv\Scripts\python.exe tools\collect_forevermart_data.py
```

Then regenerate the micro/macro reports and prepare the website again. This collector performs serial GET requests; it does not create accounts or orders and is not a concurrency/load test.

The historical [complete chapter guide](docs/CHAPTER10_GUIDE.md) and [source audit](docs/SOURCE_NOTES.md) remain for source traceability. The active scope is defined by the new assigned exercise guide. Do not regenerate the frozen references just to force agreement with calculated results.

## Deploy to Vercel from GitHub

The deployment folder is **`vercel-site`**. It contains the homepage (`index.html`),
the calculator, the book report, and the Python calculation endpoint. Deploying
the repository root does not serve this homepage.

1. Prepare the current website from the project terminal:

   ```powershell
   .\.venv\Scripts\python.exe tools\prepare_vercel.py
   ```

2. Commit and push **`vercel-site/`**, **`.gitignore`**, **`tools/prepare_vercel.py`**,
   and **`README.md`** to GitHub. The deployment folder is now allowed by Git.
   Use VS Code Source Control to stage those paths, commit, and push/sync. Check
   that GitHub shows `vercel-site/index.html` and `vercel-site/vercel.json`.
   Local reports under `output/` are not needed for deployment.

3. Import the GitHub repository in Vercel using these settings:

   | Setting | Value |
   |---|---|
   | Root Directory | `vercel-site` |
   | Application / Framework Preset | **Other** |
   | Build Command | Enable Override and leave empty |
   | Output Directory | `.` (a single dot) |
   | Install Command | Leave default |
   | Environment Variables | None required |

   The prepared `vercel.json` also specifies Other, an empty build command, and
   output `.`. Python dependencies are installed for `api/calculate.py` using
   the dependency files inside `vercel-site`.

4. Click **Deploy**. For an existing Vercel project, change the Root Directory
   and build settings in **Settings → Build and Deployment**, save, then deploy
   the newest GitHub commit.

5. Check the deployed homepage, `/book-results.html`, and `/api/calculate`.
   The last address should return a JSON response containing `"status": "ready"`.
   Finally, select a book exercise in the calculator, load its book values, and
   submit it to confirm that calculations work online.

Run the preparation command and commit/push the refreshed `vercel-site/` files
after future source changes. Vercel serves the HTML interface and runs the Python
API on demand; it does not run `serve.py` as a permanent local server.

Official references: [static build settings](https://vercel.com/docs/builds/configure-a-build)
and [Python functions in `/api`](https://vercel.com/docs/functions/runtimes/python/api-directory).
