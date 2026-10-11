from pathlib import Path
import json
import re
from collections import Counter
import pypdfium2 as pdfium
from pypdf import PdfReader
import pdfplumber
from PIL import Image, ImageOps, ImageDraw

root=Path(__file__).resolve().parents[1]
pdf=root/'output/pdf/ForeverMart_Quality_Assurance_Report.pdf'
out=root/'output/forevermart-audit'
qa=root/'tmp/pdfs/forevermart-qa'
qa.mkdir(parents=True,exist_ok=True)
reader=PdfReader(str(pdf))
plan=json.loads((out/'report-page-plan.json').read_text())
records=json.loads((out/'defect-registry.json').read_text())
texts=[page.extract_text() for page in reader.pages]
problems=[]
if len(texts)!=len(plan):problems.append(f'Page count {len(texts)} differs from planned {len(plan)}')
for spec in plan:
    idx=spec['page']-1
    if idx>=len(texts):break
    text=re.sub(r'\s+',' ',texts[idx])
    if spec['kind']=='finding':
        fid=spec['title'].split()[0]
        if not text.startswith('FOREVERMART'):pass
        if fid+' /' not in text:problems.append(f'{fid} not on planned page {idx+1}')
        for field in ['Reproduction procedure','Expected result','Actual result','Recommended remedy','Retest acceptance','Evidence']:
            if field not in text:problems.append(f'{fid} missing {field} on page {idx+1}')
        if re.search(r'FM-\d{3} /',text.replace(fid+' /','')):problems.append(f'Multiple records on page {idx+1}')
with pdfplumber.open(pdf) as document:
    for i,page in enumerate(document.pages,1):
        words=page.extract_words()
        for w in words:
            if w['x0']<45 or w['x1']>568 or w['top']<15 or w['bottom']>773:
                problems.append(f'Page {i} text outside margins: {w["text"]}')
        # Body text must not cross into the page footer; header and footer are excluded.
        for w in words:
            if 741<w['bottom']<761 and w['top']>70:
                problems.append(f'Page {i} body enters footer: {w["text"]}')
pdfdoc=pdfium.PdfDocument(str(pdf))
rendered=[]
for i in range(len(pdfdoc)):
    image=pdfdoc[i].render(scale=1.4).to_pil().convert('RGB')
    dest=qa/f'page-{i+1:03d}.png';image.save(dest)
    rendered.append(dest)
for start in range(0,len(rendered),4):
    tiles=[]
    for path in rendered[start:start+4]:
        im=Image.open(path)
        tile=Image.new('RGB',(im.width,im.height+28),'#e2e4e8')
        tile.paste(im,(0,28));ImageDraw.Draw(tile).text((12,7),path.stem,fill='black')
        tiles.append(tile)
    tw,th=tiles[0].size
    sheet=Image.new('RGB',(tw*2+18,th*2+18),'#d9dde3')
    for j,tile in enumerate(tiles):sheet.paste(tile,((j%2)*(tw+18),(j//2)*(th+18)))
    sheet.save(qa/f'sheet-{start//4+1:02d}.jpg',quality=90)
result=dict(pages=len(texts),planned_pages=len(plan),defects=sum(r['classification']=='Defect' for r in records),
            observations=sum(r['classification']=='Observation' for r in records),
            rendered_pages=len(rendered),problems=problems)
(out/'layout-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
