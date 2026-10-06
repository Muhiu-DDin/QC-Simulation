"""Stage the book report, manual-entry UI, and Python calculation function."""
from pathlib import Path
import json
import re
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from qc.report_ui import CSS

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'output'
target=ROOT/'vercel-site'
target.mkdir(exist_ok=True)
report=source.joinpath('report.html').read_text(encoding='utf-8')
report=report.replace('https://vercel-site-tawny-omega.vercel.app/calculator.html','calculator.html')
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
for filename in ['calculator.html','calculator.css','calculator.js']:
    shutil.copy2(ROOT/'web'/filename,target/filename)
shutil.copy2(ROOT/'web/calculator.html',target/'index.html')
target.joinpath('report-theme.css').write_text(CSS,encoding='utf-8')
shutil.copy2(ROOT/'data/chapter10_inputs.json',target/'chapter10_inputs.json')
for folder in ['qc','data','api']:
    destination=target/folder
    destination.mkdir(exist_ok=True)
    for path in ROOT.joinpath(folder).iterdir():
        if path.is_file() and path.suffix in ('.py','.json'): shutil.copy2(path,destination/path.name)
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
print('Prepared report and online Python calculator:',target)
print('Local custom reports and the Python environment are excluded.')
