# Verification evidence

- Full numerical run: 92 cases, 92 separate PNG graphs; every HTML image link resolves.
- Independent stored references: 92 matches, zero differences.
- Book references: 24 printed self-check cases and 12 approximate OC-graph readings.
- Source comparisons: 35 matches, one preserved source erratum (SC10-5b CL=9 versus .9), zero unexplained mismatches.
- Automated tests: 12 passed, including formulas, clipping, finite-lot arithmetic, missing/changed references, input rejection and seeded reproducibility.
- Custom workflow: all three illustrative custom cases execute and produce separate reports without fabricated book comparisons.
- Comparison CSV: 271 field comparisons; reference and input hashes match the current files.
- Monte Carlo: 100,000 trials per stochastic case, seed 20260901.
- Probability estimates whose 99% interval excludes the theoretical value: SC10-9b (primary). These are reported sampling outcomes, not proof of solver failure.
- Representative mean, p, Pareto and OC graphs were visually inspected for legibility and clipping.

Dependency versions: `{"python": "3.13.7", "numpy": "2.5.3", "scipy": "1.18.1", "matplotlib": "3.11.2"}`.

This audit checks generated artifacts and internal consistency. The references labeled independently solved are not a publisher answer key. Statistical simulations rely on the models documented in README.md and SOURCE_NOTES.md.
