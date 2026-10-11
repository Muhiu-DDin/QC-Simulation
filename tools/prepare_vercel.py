"""Stage the book report, manual-entry UI, and Python calculation function."""
from pathlib import Path
import json
import re
import shutil
import sys
import subprocess
import hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from qc.report_ui import CSS
from qc.scope import assigned_cases, assignment_manifest, calculation_fingerprint
from qc.reporting import write_report

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'output'
target=ROOT/'vercel-site'
target.mkdir(exist_ok=True)
# Never publish an old all-chapter or custom report as the narrowed assignment.
book_cases=assigned_cases()
expected={case['id'] for case in book_cases}
try:
    saved=json.loads(source.joinpath('results.json').read_text(encoding='utf-8'))
    current={record['case']['id'] for record in saved['records']}
    originals={case['id']:case for case in book_cases}
    valid=current==expected and len(saved['records'])==len(book_cases)
    valid=valid and all(record['case']==originals[record['case']['id']] for record in saved['records'])
    valid=valid and saved.get('metadata',{}).get('reference_sha256')==hashlib.sha256(ROOT.joinpath('data/chapter10_answers.json').read_bytes()).hexdigest()
    valid=valid and saved.get('metadata',{}).get('input_sha256')==hashlib.sha256(ROOT.joinpath('data/chapter10_inputs.json').read_bytes()).hexdigest()
    valid=valid and saved.get('metadata',{}).get('engine_sha256')==calculation_fingerprint()
except (OSError,ValueError,KeyError,TypeError):
    valid=False
if not valid:
    subprocess.run([sys.executable,str(ROOT/'run.py'),'--strict','--trials','10000'],check=True)
else:
    # Refresh presentation without repeating a valid saved calculation.
    write_report(saved['records'],source,saved['metadata'],reuse_graphs=True)
report=source.joinpath('report.html').read_text(encoding='utf-8')
report=report.replace('https://vercel-site-tawny-omega.vercel.app/calculator.html','calculator.html')
report=report.replace('</head>','<link rel="icon" type="image/svg+xml" href="favicon.svg?v=1"></head>')
target.joinpath('book-results.html').write_text(report,encoding='utf-8')
for filename in ['comparison.csv','results.json']:
    shutil.copy2(source/filename,target/filename)
for relative in re.findall(r'<img src="([^"]+)"',report):
    asset=Path(relative)
    if asset.is_absolute() or '..' in asset.parts:
        raise ValueError('Report asset must stay within the output directory')
    destination=target/asset
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/asset,destination)
for filename in ['calculator.html','calculator.css','calculator.js','favicon.svg']:
    shutil.copy2(ROOT/'web'/filename,target/filename)
shutil.copy2(ROOT/'web/calculator.html',target/'index.html')
target.joinpath('report-theme.css').write_text(CSS,encoding='utf-8')
catalog=json.loads(ROOT.joinpath('data/chapter10_inputs.json').read_text(encoding='utf-8'))
catalog['cases']=assigned_cases(catalog['cases'])
catalog['assignment']=assignment_manifest()
target.joinpath('chapter10_inputs.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'data/forevermart_dataset_manifest.json',target/'dataset_manifest.json')
for scale in ['micro','macro']:
    shutil.copy2(ROOT/'data'/f'forevermart_{scale}.csv',target/f'forevermart_{scale}.csv')
for folder in ['qc','data','api']:
    destination=target/folder
    destination.mkdir(exist_ok=True)
    for path in ROOT.joinpath(folder).iterdir():
        if path.is_file() and path.suffix in ('.py','.json','.csv'): shutil.copy2(path,destination/path.name)
target.joinpath('data/chapter10_inputs.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
answers=json.loads(ROOT.joinpath('data/chapter10_answers.json').read_text(encoding='utf-8'))
answers['references']={key:value for key,value in answers['references'].items() if key in expected}
target.joinpath('data/chapter10_answers.json').write_text(json.dumps(answers,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'requirements.txt',target/'requirements.txt')
dependencies=[line.strip() for line in ROOT.joinpath('requirements.txt').read_text().splitlines() if line.strip() and not line.startswith('#')]
target.joinpath('pyproject.toml').write_text('[project]\nname = "qc-web-calculator"\nversion = "1.0.0"\nrequires-python = ">=3.13,<3.14"\ndependencies = '+json.dumps(dependencies)+'\n',encoding='utf-8')
target.joinpath('vercel.json').write_text(json.dumps({
    'framework':None,
    'functions':{'api/calculate.py':{'maxDuration':60,'excludeFiles':'{graphs/**,index.html,results.json,comparison.csv}'}},
    'headers':[{'source':'/(.*)','headers':[
        {'key':'X-Content-Type-Options','value':'nosniff'},
        {'key':'Referrer-Policy','value':'strict-origin-when-cross-origin'}]}]
},indent=2),encoding='utf-8')
target.joinpath('.vercelignore').write_text('.vercel\n',encoding='utf-8')
print('Prepared 22 assigned book cases and ForeverMart micro/macro calculator:',target)
print('Local custom reports and the Python environment are excluded.')
