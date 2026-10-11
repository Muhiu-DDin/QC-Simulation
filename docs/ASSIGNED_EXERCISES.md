# Assigned book exercises: 10.40-10.59

The active book calculations cover **Exercises 10.40 through 10.59 only**. The
book prints the numbers as `10-40` through `10-59`; the program keeps that spelling
in case IDs. For example, `10-47a` means Exercise 10.47, part (a).

These 20 exercises contain **11 numerical/chart exercises, represented by 22
calculation cases**, and **9 conceptual questions without supplied numerical
data**. More than one case is needed when a question has different numeric
sampling plans or different calculations. A discussion about an existing chart
does not require a duplicate numerical case.

The data tables, question subparts and OC graph were visually checked against the
supplied *Statistics for Management* PDF, printed pages 511-514 (one-based PDF
pages 526-529). The complete original input catalogue and frozen reference JSON
remain preserved. The scope selector controls which book cases are active.

| Exercise | Type | Included calculation IDs | What is covered |
|---|---|---|---|
| 10.40 | Numerical | `10-40a`, `10-40b` | Aggregate one-sided proportion test; weekly p chart and interpretation |
| 10.41 | Conceptual | None | Vital few versus trivial many; Pareto prioritisation |
| 10.42 | Conceptual | None | Two-outcome attribute coding versus four-category coding |
| 10.43 | Conceptual | None | Transaction complexity as an identifiable source of service-time variation |
| 10.44 | Numerical | `10-44` | Part (a): mean chart; part (b): assess shift pattern |
| 10.45 | Numerical | `10-45` | Part (a): range chart using 10.44 data; part (b): interpret variability |
| 10.46 | Numerical | `10-46` | Subcontractor fault counts and Pareto chart |
| 10.47 | Numerical | `10-47a`, `10-47b`, `10-47c`, `10-47d` | Producer risks for all four plans at AQL 0.01 |
| 10.48 | Numerical | `10-48a`, `10-48b`, `10-48c`, `10-48d` | Consumer risks for the same four plans at LTPD 0.015 |
| 10.49 | Conceptual | None | Reducing avoidable variation in service operations |
| 10.50 | Numerical | `10-50` | Part (a): coating mean chart; parts (b)-(c): control and last-ten-batch variability |
| 10.51 | Numerical | `10-51` | Part (a): coating range chart; parts (b)-(c): declining variability and relation to 10.50 |
| 10.52 | Numerical | `10-52` | Print-defect p chart centred on supplier target 0.001 |
| 10.53 | Conceptual | None | Producer/consumer risks and Type I/Type II errors |
| 10.54 | Conceptual | None | Candidate common and special causes of package-weight variation |
| 10.55 | Graph numerical | `10-55a`, `10-55b`, `10-55c` | Producer risks at the three given AQL values |
| 10.56 | Graph numerical | `10-56a`, `10-56b`, `10-56c` | Consumer risks at the three given LTPD values |
| 10.57 | Conceptual; no data | None | Design GPA and A/B-proportion charts; no raw GPA or grade counts supplied |
| 10.58 | Conceptual | None | Benefits and remaining risks of acceptance sampling |
| 10.59 | Conceptual; no data | None | Recommend a p chart for graduation and discuss limitations; no cohort data supplied |

## Inputs, answers and simulation

- `data/chapter10_inputs.json` retains the original book-data catalogue. It is not
  rewritten during calculation.
- `data/chapter10_answers.json` retains the frozen references. Regular-exercise
  references were independently solved; they are **not publisher answers**.
- Exercises 10.55 and 10.56 additionally compare with approximate readings of the
  printed graph. The graph tolerance is 0.02 in probability. The project uses a
  Poisson approximation consistent with that graph, explicitly as an inference,
  and also reports the binomial value.
- Python first calculates the formula result. Monte Carlo simulation provides an
  additional numerical estimate or model check. It does not turn simulated data
  into real observations or make an independent reference into a printed answer.
- Exercises 10.44/10.45 and 10.50/10.51 deliberately share source datasets because
  the book asks for complementary mean and range charts.
- Conceptual explanations in `data/assignment_scope.json` are project-written
  guidance. They are not copied answers or invented numerical datasets.

For 10.48, a 2,500-item lot at 0.015 defective has an implied 37.5 defectives.
The requested binomial approximation is valid, but an exact fixed-lot
hypergeometric calculation requires a specified integer defective count.
The program does not silently round 37.5.

## How the scope is selected

`qc/scope.py` exposes:

```python
from qc.scope import assigned_cases, assignment_manifest, in_assignment

cases = assigned_cases()       # 22 cases, in exercise order
manifest = assignment_manifest()  # all 20 exercises, including no-data questions
assert in_assignment("10-40a")
assert not in_assignment("SC10-1a")
```

`assigned_cases(existing_cases)` can filter a catalogue already loaded by a
caller. It retains the source IDs and input values. The assigned numerical scope
and independently supplied micro/macro datasets are separate sources; custom
data have no textbook answer unless the same stored numerical inputs are
explicitly selected for comparison.
