"""Refresh existing report presentation without rerunning statistical experiments."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from qc.reporting import write_report

for path in sorted(ROOT.joinpath('output').rglob('results.json')):
    saved=json.loads(path.read_text(encoding='utf-8'))
    write_report(saved['records'],path.parent,saved['metadata'],reuse_graphs=True)
    print('Updated',path.parent.relative_to(ROOT)/'report.html')
