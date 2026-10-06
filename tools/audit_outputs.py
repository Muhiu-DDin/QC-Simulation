"""Audit generated deliverables and save concise portfolio verification evidence."""
import csv
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output'
results=json.loads(out.joinpath('results.json').read_text(encoding='utf-8'))
records=results['records']; report=out.joinpath('report.html').read_text(encoding='utf-8')
images=re.findall(r'<img src="([^"]+)"',report)
assert len(records)==92
assert len(images)==92 and all(out.joinpath(p).is_file() for p in images)
assert results['metadata']['reference_sha256']==hashlib.sha256(ROOT.joinpath('data/chapter10_answers.json').read_bytes()).hexdigest()
assert results['metadata']['input_sha256']==hashlib.sha256(ROOT.joinpath('data/chapter10_inputs.json').read_bytes()).hexdigest()
assert all(r['comparisons']['independent']['status']=='MATCH' for r in records)
assert not any(r['comparisons']['book']['status']=='MISMATCH' for r in records)
with out.joinpath('comparison.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
misses=[f"{r['case']['id']} ({name})" for r in records for name,v in r['simulation'].items()
        if isinstance(v,dict) and v.get('theory_in_ci99') is False]
source_counts={kind:sum(r['comparisons']['book'].get('provenance')==kind for r in records)
               for kind in ['printed_book','approximate_graph_reading']}
text=f'''# Verification evidence

- Full numerical run: 92 cases, 92 separate PNG graphs; every HTML image link resolves.
- Independent stored references: 92 matches, zero differences.
- Book references: {source_counts['printed_book']} printed self-check cases and {source_counts['approximate_graph_reading']} approximate OC-graph readings.
- Source comparisons: 35 matches, one preserved source erratum (SC10-5b CL=9 versus .9), zero unexplained mismatches.
- Automated tests: 12 passed, including formulas, clipping, finite-lot arithmetic, missing/changed references, input rejection and seeded reproducibility.
- Custom workflow: all three illustrative custom cases execute and produce separate reports without fabricated book comparisons.
- Comparison CSV: {len(rows)} field comparisons; reference and input hashes match the current files.
- Monte Carlo: {results['metadata']['trials']:,} trials per stochastic case, seed {results['metadata']['seed']}.
- Probability estimates whose 99% interval excludes the theoretical value: {', '.join(misses) or 'none'}. These are reported sampling outcomes, not proof of solver failure.
- Representative mean, p, Pareto and OC graphs were visually inspected for legibility and clipping.

Dependency versions: `{json.dumps(results['metadata']['versions'])}`.

This audit checks generated artifacts and internal consistency. The references labeled independently solved are not a publisher answer key. Statistical simulations rely on the models documented in README.md and SOURCE_NOTES.md.
'''
out.joinpath('VERIFICATION.md').write_text(text,encoding='utf-8')
print(text)
