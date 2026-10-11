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

## Part 2C — ForeverMart micro and macro data

Select **Micro / macro data · Part 2C**, then choose the scale:

| Recorded dataset | Scope | Batches | Actual HTTP checks |
|---|---|---:|---:|
| Micro | Focused homepage observations | 20 | 60 |
| Macro | Broader observations across eight public routes | 100 | 300 |

These are **real, dated measurements from https://forevermart.vercel.app/**, recorded on 11 October 2026. Each CSV row contains three sequential checks and their mean response time. A check passes when it returns HTTP 200, HTML content and the React root element. All 360 checks in this capture passed that narrow criterion. This does not establish that browser interactions, shopping, login or checkout work.

The macro dataset is larger and has wider coverage than the micro dataset; **100 batches are not an industrial Big Data dataset**. For larger real datasets, import your own CSV, up to 20,000 batches and 2 MB per request. The optional synthetic example supplies 10,000 teaching batches and is explicitly labelled synthetic; it is separate from the ForeverMart measurements.

The analysis includes:

- Count-weighted pass/failure rates and 95% Wilson intervals.
- A p chart with subgroup-specific limits when batch sizes differ.
- Ordered batch response times and a histogram of batch means.
- An editable timing threshold; 500 ms is a study target, not an established website SLA.
- Exact binomial probability compared with Monte Carlo estimates.
- Empirical response-time resampling compared with the calculated weighted mean.
- Dataset provenance, model assumptions and practical investigation steps.

The recorded all-pass data give a fitted failure probability of zero. The report shows the Wilson upper bound and explains why zero observed failures is not proof of zero risk. Timing resampling still verifies the empirical mean. More simulation trials reduce simulation noise; they do not collect more real website evidence.

To generate standalone mini-project reports:

```powershell
.\.venv\Scripts\python.exe run.py --project micro
.\.venv\Scripts\python.exe run.py --project macro
```

Open `output/forevermart-micro/report.html` and `output/forevermart-macro/report.html`. Both include two exported PNG charts and complete JSON results. These runs do not overwrite the book report.

## Use your own dataset

In the dataset form choose **My own CSV data**, then upload or paste a CSV using exactly these columns:

```csv
period,passed,failed,response_ms
batch-001,98,2,240.5
batch-002,95,5,310.8
```

`period` is a unique ordered batch label. `passed` and `failed` are nonnegative whole outcome counts whose sum must be positive. `response_ms` is the positive **mean** response time for that same batch. The example above is illustrative, not additional ForeverMart evidence.

You may change the response-time threshold and run one dataset analysis at a time. Own-data results show **Independent data** and never compare against textbook answers. [The mini-project guide](docs/MINI_PROJECTS.md) explains collection, formulas and interpretation.

CLI equivalent:

```powershell
.\.venv\Scripts\python.exe run.py --project macro --dataset my_data.csv --threshold-ms 700 --output output\my-dataset
```

For individual custom numerical exercises, the existing JSON input format remains available:

```powershell
.\.venv\Scripts\python.exe run.py --input examples\custom_inputs.json --output output\custom
```

## Files and responsibilities

| Location | Purpose |
|---|---|
| `data/chapter10_inputs.json` | Preserved full source transcription; runtime assignment filter selects 10.40–10.59 |
| `data/chapter10_answers.json`, `book_answers.py` | Preserved frozen answers and their provenance; never generated from runtime results |
| `data/assignment_scope.json`, `qc/scope.py` | Active exercise range and numerical/conceptual coverage |
| `data/forevermart_micro.csv`, `data/forevermart_macro.csv` | Actual website measurement batches |
| `data/forevermart_http_checks.json` | Raw evidence for every recorded request |
| `data/forevermart_dataset_manifest.json` | Collection dates, routes, definitions and file hashes |
| `qc/calculations.py`, `qc/simulation.py`, `qc/comparison.py` | Numerical formulas, sampling models and reference comparisons |
| `qc/dataset_projects.py` | Independent dataset validation, analysis, charts and simulations |
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

The collector can refresh the real website sample; doing so intentionally changes the dated evidence and its hashes:

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
