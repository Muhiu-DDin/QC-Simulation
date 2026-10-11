"""Add a full page-two contents list while preserving the owner's edited PDF."""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import re

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject, TextStringObject
from pypdf.annotations import Link
import pdfplumber
import pypdfium2 as pdfium
from PIL import ImageChops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/Muhiddin/OneDrive/Desktop/ForeverMart_Quality_Assurance_Report (1).pdf')
OUTPUT = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_With_Contents.pdf'
QA = ROOT / 'tmp/pdfs/forevermart-contents'
QA.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('ContentsArial', str(FONT_DIR / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('ContentsArialBold', str(FONT_DIR / 'arialbd.ttf')))
pdfmetrics.registerFontFamily('ContentsArial', normal='ContentsArial', bold='ContentsArialBold')
INK = HexColor('#252830')
GRAY = HexColor('#657080')
RED = HexColor('#B92F3B')
RULE = HexColor('#D5D8DE')
FN, FB = 'ContentsArial', 'ContentsArialBold'

source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
reader = PdfReader(SOURCE)
assert len(reader.pages) == 117
assert 'Ghulam Mohiuddin' in reader.pages[0].extract_text()
assert 'B22110106023' in reader.pages[0].extract_text()
assert '1 Executive summary' in reader.pages[1].extract_text()
assert '2 Contents and reading guide' in reader.pages[2].extract_text()

plan = json.loads((ROOT / 'output/forevermart-audit/report-page-plan.json').read_text())
entries = []
for spec in plan:
    if spec['kind'] != 'section' or spec['page'] == 3:
        continue
    title = re.sub(r'^\d+\s+', '', spec['title'])
    if title.startswith('Finding index'):
        if spec['page'] != 17:
            continue
        entries.append(('Complete finding index', '17-19', 16))
        entries.append(('Detailed finding records: FM-001 to FM-090', '20-109', 19))
    else:
        page = 3 if spec['page'] == 2 else spec['page']
        entries.append((title, str(page), page - 1))
assert len(entries) == 24

buffer = BytesIO()
c = canvas.Canvas(buffer, pagesize=(612, 792), pageCompression=1)
c.setFillColor(GRAY)
c.setFont(FB, 8)
c.drawString(48, 763, 'FOREVERMART')
c.drawRightString(564, 763, 'SOFTWARE TESTING | PORTFOLIO PART 3')
c.setStrokeColor(RULE)
c.setLineWidth(.5)
c.line(48, 752, 564, 752)
c.setFillColor(RED)
c.setFont(FB, 9)
c.drawString(48, 729, 'REPORT NAVIGATION')
c.setFillColor(INK)
c.setFont(FB, 24)
c.drawString(48, 699, 'Table of contents')
c.setFillColor(GRAY)
c.setFont(FN, 9)
c.drawString(48, 679, 'Page numbers refer to the numbered pages of this report.')
c.setFillColor(INK)
c.setFont(FB, 9)
c.drawString(48, 657, 'Section')
c.drawRightString(564, 657, 'Page')
c.setStrokeColor(RED)
c.setLineWidth(1)
c.line(48, 649, 564, 649)

link_rects = []
y = 632
for title, pages, destination in entries:
    c.setFillColor(INK)
    c.setFont(FN, 9.25)
    c.drawString(48, y, title)
    c.setFillColor(RED)
    c.setFont(FB, 9.25)
    c.drawRightString(564, y, pages)
    start = 48 + pdfmetrics.stringWidth(title, FN, 9.25) + 8
    end = 564 - pdfmetrics.stringWidth(pages, FB, 9.25) - 8
    if end > start:
        c.setStrokeColor(RULE)
        c.setLineWidth(.4)
        c.setDash(1, 2)
        c.line(start, y + 2, end, y + 2)
        c.setDash()
    link_rects.append(((48, y - 3, 564, y + 11), destination))
    y -= 15.7

c.setStrokeColor(RULE)
c.line(48, y + 4, 564, y + 4)
y -= 16
c.setFillColor(INK)
c.setFont(FB, 11)
c.drawString(48, y, 'Reading guide')
y -= 17
notes = [
    ('How to read each finding', 'Each record gives an identifier, a matching test reference, affected module and URL, discovery method, severity, priority, preconditions, reproduction procedure, expected result, actual result, impact, recommended remedy, retest acceptance and evidence paths.'),
    ('Status and responsibility', 'Open means the defect has been reported and has no verified repair. Review required means an observation needs a product decision. Owner roles are proposed, not assignments to named individuals. Developer and client responses have not been supplied.'),
    ('Classification discipline', 'Repeated symptoms in a shared implementation are grouped where appropriate. Footer links form one defect, repeated missing product names form one defect, and copied template content forms one defect. Separate server rules such as quantity, product existence, price and total are retained because they require separate validation and regression assertions.'),
]
style = ParagraphStyle('ReadingGuide', fontName=FN, fontSize=8.35, leading=10.6, textColor=INK)
for title, text in notes:
    p = Paragraph(f'<b>{title}.</b> {text}', style)
    _, height = p.wrap(516, 792)
    p.drawOn(c, 48, y - height)
    y -= height + 7
caption = Paragraph('Finding labels and classifications follow the intent of Lewis Chapter 24 and Appendices E12/E27, with terminology adapted to this storefront.', ParagraphStyle('Caption', fontName=FN, fontSize=7.4, leading=9.3, textColor=GRAY))
_, height = caption.wrap(516, 792)
caption.drawOn(c, 48, y - height)
assert y - height >= 52, f'Contents page overflow: bottom={y-height}'
c.setStrokeColor(RULE)
c.line(48, 42, 564, 42)
c.setFillColor(GRAY)
c.setFont(FN, 8.05)
c.drawString(48, 26.1, 'Quality assurance audit | 9 October 2026 | Version 1.0')
c.drawRightString(555.16, 26.1, '2')
c.showPage()
c.save()
toc_reader = PdfReader(buffer)

# Importing in the new order preserves the PDF's original annotations and maps
# its existing outline destinations to the moved pages.
writer = PdfWriter()
writer.append(reader, pages=[0, 2, 1] + list(range(3, 117)), import_outline=True)
toc = toc_reader.pages[0].clone(writer)
new_toc = writer.pages[1]
for key in ('/Contents', '/Resources', '/MediaBox', '/CropBox'):
    if key in toc:
        new_toc[NameObject(key)] = toc.raw_get(key)
new_toc.pop(NameObject('/Annots'), None)

# Remove only the old executive-summary footer numeral, using the precise text
# block position in the attached WPS-exported document. All body text is retained.
summary = writer.pages[2]
stream = ContentStream(summary['/Contents'], writer)
ops = stream.operations
result = []
removed = 0
i = 0
while i < len(ops):
    if ops[i][1] == b'BT':
        end = i + 1
        while end < len(ops) and ops[end][1] != b'ET':
            end += 1
        assert end < len(ops)
        block = ops[i:end + 1]
        footer_number = any(op == b'Tm' and abs(float(args[4]) - 550.68) < .2 and abs(float(args[5]) - 765.89) < .2 for args, op in block)
        if footer_number:
            removed += 1
        else:
            result.extend(block)
        i = end + 1
    else:
        result.append(ops[i])
        i += 1
assert removed == 1
stream.operations = result
summary[NameObject('/Contents')] = writer._add_object(stream)
number_buffer = BytesIO()
n = canvas.Canvas(number_buffer, pagesize=(612, 792))
n.setFillColor(GRAY)
n.setFont(FN, 8.05)
n.drawString(550.68, 26.11, '3')
n.save()
summary.merge_page(PdfReader(number_buffer).pages[0])

for rect, destination in link_rects:
    writer.add_annotation(page_number=1, annotation=Link(rect=rect, target_page_index=destination))
    # Local PDF destinations use a page reference, for broad viewer compatibility.
    writer.pages[1]['/Annots'][-1].get_object()['/Dest'][0] = writer.pages[destination].indirect_reference

def rename_outline(node):
    while node:
        obj = node.get_object()
        if obj.get('/Title') == '2 Contents and reading guide':
            obj[NameObject('/Title')] = TextStringObject('Table of contents')
        if obj.get('/First'):
            rename_outline(obj['/First'])
        node = obj.get('/Next')

if writer.root_object.get('/Outlines'):
    rename_outline(writer.root_object['/Outlines'].get('/First'))
metadata = {key: str(value) for key, value in reader.metadata.items() if value is not None}
metadata['/Title'] = 'ForeverMart Software Quality Assurance Report - Table of Contents'
writer.add_metadata(metadata)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('wb') as f:
    writer.write(f)

final = PdfReader(OUTPUT)
assert len(final.pages) == 117
assert 'Table of contents' in final.pages[1].extract_text()
assert '1 Executive summary' in final.pages[2].extract_text()
assert final.pages[0].extract_text() == reader.pages[0].extract_text()
for index in range(3, 117):
    assert final.pages[index].extract_text() == reader.pages[index].extract_text(), f'Body text changed on page {index+1}'
for title, pages, destination in entries:
    assert title in final.pages[1].extract_text()
    assert pages in final.pages[1].extract_text()
assert len(final.pages[1]['/Annots']) == 24
page_refs = {page.indirect_reference.idnum: index for index, page in enumerate(final.pages)}
actual_destinations = [page_refs[a.get_object()['/Dest'][0].idnum] for a in final.pages[1]['/Annots']]
assert actual_destinations == [destination for _, _, destination in entries]

# Render every unchanged page against the source and compare pixels. Inspect the
# two edited pages at a higher resolution in the next tool step.
source_pdf = pdfium.PdfDocument(str(SOURCE))
final_pdf = pdfium.PdfDocument(str(OUTPUT))
differences = []
for index in range(117):
    if index in (1, 2):
        continue
    original = source_pdf[index].render(scale=.65).to_pil().convert('RGB')
    actual = final_pdf[index].render(scale=.65).to_pil().convert('RGB')
    if ImageChops.difference(original, actual).getbbox():
        differences.append(index + 1)
assert not differences, f'Unexpected visual changes: {differences}'
for index in (0, 1, 2, 3):
    final_pdf[index].render(scale=1.5).to_pil().save(QA / f'page-{index+1:03d}.png')

with pdfplumber.open(OUTPUT) as f:
    toc_words = f.pages[1].extract_words()
    assert all(w['x0'] >= 46 and w['x1'] <= 566 for w in toc_words)
    footer = [w['text'] for w in f.pages[2].extract_words() if w['top'] > 750 and w['x0'] > 540]
    assert footer == ['3'], footer

assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
checks = dict(source=str(SOURCE), output=str(OUTPUT), pages=117, contents_page=2,
              executive_summary_page=3, linked_entries=24,
              unchanged_pages_pixel_verified=115, unexpected_visual_changes=differences,
              source_preserved=True, contents_bottom_y=round(y-height, 2))
(QA / 'verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
