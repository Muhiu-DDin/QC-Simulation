# Source audit and statistical choices

Source: user-supplied *Statistics for Management*, Chapter 10, “Quality and Quality Control.” The preface identifies the eighth edition. Source filename:

`feismo.com-statistics-for-management-by-richard-i-levin-z-liborgpdf-pr_a5ff80c2224b12454656623b64822df2.pdf`

Chapter: printed pp.465-515 = one-based PDF pp.480-530. Appendix Table 9: printed p.972 = PDF p.987. The offset is +15 within these sections. Source page numbers accompany each input and printed reference. PDF extraction has malformed embedded-font text in some passages; ambiguous numbers, tables and graph readings were checked visually.

## Answer availability

The book prints worked answers for SC10-1 through SC10-9 inside the chapter. There is no regular-exercise answer key in the supplied PDF. Never present the independent references for Exercises 10-12, 10-13, etc. as publisher answers. The graphical questions 10-38/39 and 10-55/56 can be compared against visually read graph ordinates, with lower precision.

## Errors and rounding in the source

| Location | Source issue | Treatment |
|---|---|---|
| SC10-5(b), printed p.493 | Worked line says `CL = p = 9`, although input and subsequent arithmetic use .9 | Store raw CL=9 and flag `SOURCE_ERRATUM`; engine and independent reference calculate .9. A probability cannot be 9. |
| SC10-8(c), printed p.507 | Intermediate line subtracts .1330 rather than the preceding .3688, yet final result is .2642 | Preserve final .2642 with rounded-probability tolerance and explain the incorrect intermediate line. |
| Acceptance example, printed p.502 | c=0 sentence appears to reverse exact/approximate consumer risks | For N=1000,D=20,n=100,c=0: binomial is .13261956; hypergeometric is about .1190. This worked-example prose is not used as a reference for exercise cases. |
| SC10-6, printed p.494 | Reference uses p=.898 after rounding; input percentages are rounded to two decimals | Retain percentages as printed and allow .0006 absolute comparison error. No fictitious exact counts are created. |
| 10-25 table, printed p.492 | Header says “Percent correct”, but entries are fractions (.89 etc.) | Treat entries as proportions; do not divide them by 100 again. |
| 10-12(a), printed p.478 | Given sigma-xbar=1.2 is already a standard error | Use CL +/- 3*1.2; dividing again by sqrt(12) would be incorrect. |

Printed numbers are finite-precision approximations. For example, SC10-9 combines separately rounded probabilities. The reference tolerance is slightly larger than half the final unit where cumulative intermediate rounding needs it; tolerances are recorded and visible for every field.

## Control-chart formulas

- Mean: CL = grand mean; UCL/LCL = grand mean +/- 3*Rbar/(d2*sqrt(n)). With known standard error, use +/-3*SE.
- Range: CL = Rbar; LCL = D3*Rbar; UCL = D4*Rbar. D3 is zero for n<=6 in the appendix.
- Proportion: CL = specified target p, or the observed overall fraction if no target is given; limits = p +/-3*sqrt(p*(1-p)/n), clipped to [0,1].
- Positive lower range limit identity: UCL = 2*Rbar-LCL. A clipped zero LCL does not uniquely determine UCL without n/factors.
- All exercise subgroups are equal-sized. A future unequal-sized p chart needs weighted pooled p and subgroup-specific limits; this implementation rejects inconsistent raw subgroup widths rather than using a misleading equal-size formula.

Mean charts use d2-based Equation 10-2; range charts use the rounded D3/D4 appendix values. Using rounded A2 instead of recomputing 3/(d2*sqrt(n)) can slightly change the last digit. The complete appendix factors n=2..25 are transcribed in `qc/calculations.py`.

The chapter recommends inspecting outliers, trends, shifts, cycles, hugging limits and hugging the center. The report adds explicit eight-on-one-side and six-strictly-monotonic rules as **supplementary project diagnostics**. They do not detect every cycle or change of spread, and they are not represented as rules supplied by the textbook.

## Acceptance distributions

The chapter's producer's risk models the supplier's output stream as binomial: alpha = P(X>c) at AQL. The requested consumer's approximation is beta = P(X<=c) for a binomial X at LTPD. Thus N does not enter that binomial formula.

A **fixed** lot inspected without replacement instead has X ~ Hypergeometric(N,D,n). The software additionally reports that risk where D=N*p is an integer. For example, .015*2500=37.5 and .005*2500=12.5 are not valid fixed-lot defective counts. The project does not silently choose 37 or 38, or 12 or 13. These inputs remain perfectly meaningful as process probabilities in binomial/Poisson models.

The printed OC graphs at pp.506 and 514 are consistent with Poisson approximations, as used in the chapter's spreadsheet discussion at p.503. This is an **inference from the ordinates**, not an explicit formula stated beside each exercise graph:

- n=250,c=2,p=.01 gives Poisson acceptance .543813, consistent with the plotted roughly .54.
- n=300,c=3,p=.01 gives Poisson acceptance .647232, consistent with the plotted roughly .65.

For those graph-reading exercises the primary simulation/reference uses Poisson with lambda=n*p. The report also calculates binomial probabilities and plots hypergeometric curves at valid discrete defective counts. Visual reference tolerance is .02 in probability. These graph readings must not be reported as four-decimal book answers.

## Aggregate hypothesis tests

10-26(a): H0 p=.015; H1 p>.015, using 16,000 capsules. 10-40(a): H0 p=.02; H1 p>.02, using 2,000 clients. The normal z-test uses the null standard error. The project chooses alpha=.05 because the exercise does not specify it; both p-values and exact one-sided binomial p-values are reported so another alpha can be used.

Failing to reject H0 does not establish certainty or demonstrate compliance. Likewise, stable control-chart behavior does not show that a process meets customer requirements, and individual specification bounds must not be drawn as if they were subgroup control limits.

## Reference integrity

Reference generation uses standard-library `math` and independently transcribed needed factors, without importing the runtime solver. Frozen reference JSON is read-only during `run.py`; its hash is recorded in each result report. This prevents accidental runtime self-comparison. Both implementations share the mathematical source, so human source review and edge-case tests remain important.

The project does not provide a fabricated 100-defect QA report or real observations for Part 2C. Its illustrative custom-input data are labeled synthetic.
