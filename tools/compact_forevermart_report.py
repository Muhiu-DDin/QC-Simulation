"""Reflow the existing audit continuously without changing its findings."""
from pathlib import Path
from collections import Counter
from html import escape
import ast
import hashlib
import json
import math
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                               Table, TableStyle, Spacer, PageBreak, Image, Flowable,
                               KeepTogether, CondPageBreak)
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Circle, PolyLine
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
import pdfplumber
import pypdfium2 as pdfium
from PIL import Image as PILImage, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/forevermart-audit'
QA = ROOT / 'tmp/pdfs/forevermart-compact'
FINAL = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_Compact.pdf'
SOURCE = Path('C:/Users/Muhiddin/OneDrive/Desktop/ForeverMart_Quality_Assurance_Report_With_Contents.pdf')
QA.mkdir(parents=True, exist_ok=True)
R = json.loads((OUT / 'defect-registry.json').read_text(encoding='utf-8'))
D = [r for r in R if r['classification'] == 'Defect']
O = [r for r in R if r['classification'] == 'Observation']
assert len(D) == 70 and len(O) == 20
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
cover_text = PdfReader(SOURCE).pages[0].extract_text()
assert 'Ghulam Mohiuddin' in cover_text and 'B22110106023' in cover_text

FONT_DIR = Path('C:/Windows/Fonts')
FN, FB = 'AuditArial', 'AuditArialBold'
pdfmetrics.registerFont(TTFont(FN, str(FONT_DIR / 'arial.ttf')))
pdfmetrics.registerFont(TTFont(FB, str(FONT_DIR / 'arialbd.ttf')))
pdfmetrics.registerFontFamily(FN, normal=FN, bold=FB, italic=FN, boldItalic=FB)
RED = colors.HexColor('#B92F3B')
INK = colors.HexColor('#252830')
GRAY = colors.HexColor('#657080')
PALE = colors.HexColor('#F3F4F6')
BORDER = colors.HexColor('#D5D8DE')
WIDTH = 516
PW, PH = A4
LEFT, TOP, BOTTOM = 40, 58, 51

styles = {}
def style(name, size, leading, **kwargs):
    styles[name] = ParagraphStyle(name, fontName=FN, fontSize=size, leading=leading,
                                  textColor=INK, spaceAfter=7, **kwargs)

style('BodyReport', 12, 16.3)
style('SmallReport', 10.2, 13.5)
styles['SmallReport'].textColor = GRAY
style('CellReport', 10.6, 13.8, spaceBefore=0)
styles['CellReport'].spaceAfter = 0
style('CellHeadReport', 10.6, 13.8)
styles['CellHeadReport'].fontName = FB
styles['CellHeadReport'].textColor = colors.white
styles['CellHeadReport'].spaceAfter = 0
style('H1Report', 23, 28)
styles['H1Report'].fontName = FB
styles['H1Report'].spaceAfter = 15
style('H2Report', 13, 17, spaceBefore=8)
styles['H2Report'].fontName = FB
style('FindingTitle', 20, 24)
styles['FindingTitle'].fontName = FB
styles['FindingTitle'].spaceAfter = 10
style('EvidenceTitle', 17, 21)
styles['EvidenceTitle'].fontName = FB
styles['EvidenceTitle'].spaceAfter = 8
style('FindingSection', 12, 15.5, spaceBefore=5)
styles['FindingSection'].fontName = FB
styles['FindingSection'].spaceAfter = 4
style('FindingBody', 11.8, 15.6)
styles['FindingBody'].spaceAfter = 5
style('Kicker', 10.5, 14)
styles['Kicker'].fontName = FB
styles['Kicker'].textColor = RED
style('RegisterCell', 11.2, 14.5)
styles['RegisterCell'].spaceAfter = 0
style('CoverTitle', 38, 44)
styles['CoverTitle'].fontName = FB
style('CoverSub', 18, 25)
style('CoverMeta', 13, 20)
for name in ['H1Report', 'H2Report', 'FindingTitle', 'FindingSection', 'EvidenceTitle', 'Kicker']:
    styles[name].keepWithNext = True
styles['H1Report'].spaceBefore = 15
styles['H1Report'].spaceAfter = 10
styles['FindingTitle'].spaceBefore = 16
styles['EvidenceTitle'].spaceBefore = 15

def clean(text):
    return str(text).replace('\u2019', "'").replace('\u2018', "'").replace('\u2013', '-').replace('\u2014', '-').replace('\u00a0', ' ')

def p(text, style_name='BodyReport'):
    return Paragraph(escape(clean(text)).replace('\n', '<br/>'), styles[style_name])

def htmlp(text, style_name='BodyReport'):
    return Paragraph(text, styles[style_name])

def label(title, text, style_name='FindingBody'):
    return htmlp('<b>' + escape(title) + '</b> ' + escape(clean(text)), style_name)

def h2(text):
    return p(text, 'H2Report')

def caption(text):
    return p(text, 'SmallReport')

def table(rows, widths=None, header=True, size='CellReport'):
    if header and 'Authenticated' in rows[0]:
        rows = [[('Signed in' if cell == 'Authenticated' else cell) for cell in rows[0]]] + rows[1:]
    cells = [[p(c, 'CellHeadReport' if header and i == 0 else size)
              for c in row] for i, row in enumerate(rows)]
    result = Table(cells, colWidths=widths or [WIDTH / len(rows[0])] * len(rows[0]),
                   hAlign='LEFT', repeatRows=1 if header else 0)
    commands = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), .35, BORDER)]
    if header:
        commands += [('BACKGROUND', (0, 0), (-1, 0), INK),
                     ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, PALE])]
    else:
        commands += [('ROWBACKGROUNDS', (0, 0), (-1, -1), [PALE, colors.white])]
    result.setStyle(TableStyle(commands))
    return result

def enlarge(drawing):
    def visit(node):
        if isinstance(node, String):
            node.fontSize = max(10.4, node.fontSize)
        for child in getattr(node, 'contents', []):
            visit(child)
    visit(drawing)
    # The original charts reserved full-height canvases even when only three
    # bars were present. Crop empty canvas margins without shrinking labels.
    bounds = drawing.getBounds()
    if bounds is not None:
        _, bottom, _, top = bounds
        trimmed = Drawing(WIDTH, top-bottom+20)
        drawing.translate(0, 10-bottom)
        trimmed.add(drawing)
        return trimmed
    return drawing

# Reuse the already-audited explanations and original data-driven figures. The
# old builder is parsed, never imported or run, so existing artifacts are preserved.
old_tree = ast.parse((ROOT / 'tools/build_forevermart_report.py').read_text(encoding='utf-8'))
figure_names = {'arrow', 'node', 'bars', 'pareto', 'flow_purchase', 'lifecycle', 'fishbone', 'pdca'}
env = dict(globals())
for node in old_tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in figure_names:
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<existing audit diagrams>', 'exec'), env)
for name in figure_names - {'arrow', 'node'}:
    original = env[name]
    def wrap(*args, _fn=original, **kwargs):
        if args and args[1:2] == ('Current record status',):
            kwargs['height'] = 155
        return enlarge(_fn(*args, **kwargs))
    env[name] = wrap
env['sev'] = Counter(r['severity'] for r in D)
env['cats'] = Counter(r['category'] for r in D)
env['mods'] = Counter(r['module'] for r in D)

def lifecycle_revised():
    d = Drawing(WIDTH, 255)
    node, arrow = env['node'], env['arrow']
    for x, text in [(0,'New'), (132,'Triage\nauthorise'), (264,'Assigned\nfix'), (396,'Ready\nfor retest')]:
        node(d,x,170,116,47,text)
        if x < 396:
            arrow(d,x+116,193,x+132,193)
    node(d,396,73,116,47,'QA retest')
    node(d,198,73,116,47,'Closed\nwith evidence')
    node(d,0,73,116,47,'Reopened\nreturn to fix')
    arrow(d,454,170,454,120)
    arrow(d,396,96,314,96)
    d.add(String(347,108,'Pass',fontName=FN,fontSize=10.4))
    arrow(d,454,73,454,48)
    arrow(d,454,48,58,48)
    arrow(d,58,48,58,73)
    d.add(String(320,34,'Fail',fontName=FN,fontSize=10.4))
    arrow(d,58,120,58,142)
    arrow(d,58,142,322,142)
    arrow(d,322,142,322,170)
    d.add(String(0,12,'Triage may mark Duplicate, Works as intended or New requirement with a reason.',fontName=FN,fontSize=10.4,fillColor=GRAY))
    return enlarge(d)

env['lifecycle'] = lifecycle_revised

fishbone_original = env['fishbone']
def fishbone_clean():
    drawing = fishbone_original()
    def visit(node):
        if isinstance(node, Line) and node.y1 == 143 and node.y2 > 143:
            node.y2 = 188  # Leave a clear gap below the two-line branch labels.
        for child in getattr(node, 'contents', []):
            visit(child)
    visit(drawing)
    return drawing
env['fishbone'] = fishbone_clean
env['refs'] = [
    ('W3C WCAG 2.2 Labels or Instructions', 'https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html'),
    ('W3C WCAG 2.2 Keyboard', 'https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html'),
    ('W3C WCAG 2.2 Name Role Value', 'https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html'),
    ('W3C WCAG 2.2 Contrast Minimum', 'https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html'),
    ('W3C WCAG 2.2 Reflow', 'https://www.w3.org/WAI/WCAG22/Understanding/reflow.html'),
    ('OWASP REST Security Cheat Sheet', 'https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html'),
    ('MDN Content Security Policy', 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy'),
]

class Heading(Paragraph):
    def __init__(self, title, key, style_name='H1Report'):
        super().__init__(escape(title), styles[style_name])
        self.section_key = key
        self.section_title = title

class SectionEnd(Flowable):
    """Zero-height marker records the actual end, including split tables."""
    def __init__(self, key):
        super().__init__()
        self.section_key = key
        self.width = self.height = 0
    def draw(self):
        pass

class AuditDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=LEFT, rightMargin=PW-LEFT-WIDTH,
                         topMargin=TOP, bottomMargin=BOTTOM, title='ForeverMart Quality Assurance Report',
                         author='Ghulam Mohiuddin', subject='Software Testing - Portfolio Part 3', pageCompression=1)
        self.section_pages = {}
        self.section_ends = {}
        self.section_order = []
        self.active_section = None
        self.page_start_section = None
        self.page_starts_with_continuation = False
        frame = Frame(LEFT, BOTTOM, WIDTH, PH-TOP-BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='Audit', frames=frame, onPageEnd=self.decorate))

    def beforePage(self):
        self.page_start_section = None
        self.page_starts_with_continuation = False

    def decorate(self, c, doc):
        c.saveState()
        if doc.page > 1:
            c.setFillColor(GRAY)
            c.setFont(FB, 9.5)
            c.drawString(LEFT, PH-31, 'FOREVERMART')
            c.setFont(FN, 9.5)
            header = 'QUALITY ASSURANCE REPORT'
            if self.page_starts_with_continuation:
                key = self.page_start_section or ''
                if key.startswith('FM-'):
                    header = key + ' | CONTINUED'
                elif key == 'bugs':
                    header = 'BUG REGISTER | CONTINUED'
                elif key == 'observations':
                    header = 'OBSERVATION REGISTER | CONTINUED'
            c.drawRightString(LEFT+WIDTH, PH-31, header)
            c.setStrokeColor(BORDER)
            c.setLineWidth(.5)
            c.line(LEFT, PH-42, LEFT+WIDTH, PH-42)
        c.setStrokeColor(BORDER)
        c.setLineWidth(.5)
        c.line(LEFT, 40, LEFT+WIDTH, 40)
        c.setFillColor(GRAY)
        c.setFont(FN, 9.4)
        c.drawString(LEFT, 25, 'Software Testing | Portfolio Part 3 | Audit: 9 October 2026')
        c.setFont(FB, 9.4)
        c.drawRightString(LEFT+WIDTH, 25, str(doc.page))
        c.restoreState()

    def afterFlowable(self, item):
        if isinstance(item, SectionEnd):
            self.section_ends[item.section_key] = self.page
            return
        if isinstance(item, Heading):
            self.active_section = item.section_key
            self.section_pages[item.section_key] = self.page
            self.section_order.append((item.section_key, self.page, item.section_title))
            self.canv.bookmarkHorizontalAbsolute(item.section_key, self.frame._y + item.height)
            if item.section_key != 'cover':
                self.canv.addOutlineEntry(item.section_title, item.section_key, level=0)
        if self.page_start_section is None and isinstance(item, (Paragraph, Table, Drawing, Image, Contents)):
            self.page_start_section = self.active_section
            self.page_starts_with_continuation = not isinstance(item, Heading)

TOC_GROUPS = []
class Contents(Flowable):
    def __init__(self, page_map, end_map):
        super().__init__()
        self.width = WIDTH
        self.height = 660
        self.page_map = page_map
        self.end_map = end_map

    def draw(self):
        c = self.canv
        c.setFont(FB, 11.5)
        c.setFillColor(INK)
        c.drawString(0, 647, 'Section')
        c.drawRightString(WIDTH, 647, 'Page')
        c.setStrokeColor(RED)
        c.setLineWidth(1)
        c.line(0, 635, WIDTH, 635)
        y = 611
        for title, first, last in TOC_GROUPS:
            start = self.page_map.get(first)
            if start is None:
                pages = '-'
            else:
                end = self.end_map.get(last, start)
                pages = str(start) if start == end else f'{start}-{end}'
            c.setFont(FN, 12)
            c.setFillColor(INK)
            c.drawString(0, y, title)
            c.setFont(FB, 12)
            c.setFillColor(RED)
            c.drawRightString(WIDTH, y, pages)
            x0 = pdfmetrics.stringWidth(title, FN, 12)+9
            x1 = WIDTH-pdfmetrics.stringWidth(pages, FB, 12)-9
            if x0 < x1:
                c.setStrokeColor(BORDER)
                c.setLineWidth(.4)
                c.setDash(1, 2)
                c.line(x0, y+3, x1, y+3)
                c.setDash()
            c.linkRect('', first, (0, y-4, WIDTH, y+14), relative=1, thickness=0)
            y -= 25
        assert y > 10, 'Contents page must remain a single dedicated page'

def extract_section(number):
    gathered = []
    def collect(title, items, **kwargs):
        gathered.append((re.sub(r'^\d+\s+', '', title), items))
    env['page'] = collect
    env['ref_paragraphs'] = []
    for node in old_tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if not isinstance(call.func, ast.Name) or call.func.id != 'page' or not call.args:
            continue
        title = call.args[0]
        if isinstance(title, ast.Constant) and isinstance(title.value, str) and title.value.startswith(str(number)+' '):
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<audited report section>', 'exec'), env)
    assert len(gathered) == 1, number
    return gathered[0]

def reference_table():
    rows = [
        ['Type', 'Technique / tool / source', 'Use in this ForeverMart audit'],
        ['Test method', 'Exploratory and state-transition testing', 'Browse, search, navigation, cart merge and related-product size state; reproduce visible failures.'],
        ['Test method', 'Boundary values, equivalence partitions and negative tests', 'Empty values, whitespace, -1 contact fields, quantity -0.5, unknown IDs and unsupported sizes.'],
        ['Test method', 'Authenticated API validation and read-back', 'Compare submitted data with saved orders/cart; expose altered prices, totals and invalid domains (FM-022 to FM-040).'],
        ['Test method', 'Keyboard, DOM and responsive inspection', 'Check control semantics, labels, focus, alternative text and 320/390 px layouts (FM-041 to FM-066).'],
        ['Test tool', 'Codex in-app browser and browser automation', 'Operate the demo site; capture screenshots, DOM snapshots, computed styles and authorised test responses.'],
        ['Inspection', 'Public JavaScript, product JSON and HTTP headers', 'Corroborate UI/data contracts, catalogue content and deployment policy; saved as raw evidence.'],
        ['Measurement', 'Python: JSON, math, counters and SHA-256', 'Calculate contrast, record totals and chart counts; validate evidence paths and file integrity.'],
        ['Analysis', 'Decision table, traceability, Pareto and module/severity charts', 'Link test rules to findings and prioritise the 70 defects using observed counts.'],
        ['Improvement', 'Cause/effect, defect lifecycle, PDCA and retest matrix', 'Structure proposed investigation, remedies, ownership and regression acceptance; repairs are not yet implemented.'],
        ['Book', 'William E. Lewis, second edition, 2005', 'Software Testing and Continuous Quality Improvement. Ch. 24; E12/E14/E27/E29; G4/G11/G13/G21/G22. See the book crosswalk.'],
        ['Standard', 'W3C WCAG 2.2', 'Keyboard, names/roles, labels, contrast and reflow criteria. Targeted checks rather than full certification.'],
        ['Guidance', 'OWASP REST Security; MDN CSP', 'Server validation, response exposure and policy-hardening remedies. Links appear in supporting references.'],
        ['Report tools', 'Python, ReportLab, pypdf, pdfplumber, PDFium and Pillow', 'Compose the document, preserve data, inspect text, render every page and verify layout. These are report tools, not defect scanners.'],
    ]
    return table(rows, [84, 172, 260])

def make_story(page_map=None, end_map=None):
    global TOC_GROUPS
    story = []
    groups = []
    def section(key, title, items, style_name='H1Report', separate=False):
        if story and separate:
            story.append(PageBreak())
        heading = Heading(title, key, style_name)
        if key.startswith('evidence-') and key != 'evidence-mobile':
            # Keep a screenshot's heading, description and image together;
            # natural packing places two compact evidence blocks on a page.
            story.append(KeepTogether([heading, *items, SectionEnd(key)]))
            return
        def table_heading(title_item, table_item):
            # Keep only the title, repeated column headings and first data row
            # together. Do not reserve a whole page for a splittable long table.
            title_item.keepWithNext = False
            table_item.wrap(WIDTH, PH)
            minimum = title_item.wrap(WIDTH, PH)[1] + title_item.getSpaceBefore() + title_item.getSpaceAfter()
            minimum += sum(table_item._rowHeights[:2]) + 2
            return CondPageBreak(minimum)
        if items and isinstance(items[0], Table) and items[0]._nrows > 4:
            story.append(table_heading(heading, items[0]))
        story.append(heading)
        # A figure and its explanatory caption travel together. Everything else
        # flows naturally, so sections and records can share available page space.
        i = 0
        while i < len(items):
            item = items[i]
            if (isinstance(item, Paragraph) and item.getKeepWithNext()
                    and i+1 < len(items) and isinstance(items[i+1], Table)
                    and items[i+1]._nrows > 4):
                story.append(table_heading(item, items[i+1]))
            if (isinstance(item, (Drawing, Image)) and i+1 < len(items)
                    and isinstance(items[i+1], Paragraph)
                    and items[i+1].style.name == 'SmallReport'):
                object.__setattr__(item, 'keepWithNext', True)
                story.extend([item, items[i+1]])
                i += 2
            else:
                story.append(item)
                i += 1
        story.append(SectionEnd(key))
    # Dedicated title page: identity and submission metadata only.
    section('cover', 'ForeverMart', [
        Spacer(1, 18), p('Software Quality Assurance Report', 'CoverTitle'),
        Spacer(1, 10), p('Software Testing - Portfolio Part 3', 'CoverSub'),
        Spacer(1, 49), p('Submitted by', 'Kicker'),
        p('Ghulam Mohiuddin', 'CoverSub'), p('Seat number: B22110106023', 'CoverMeta'),
        Spacer(1, 19), p('Course', 'Kicker'),
        p('Software Quality Engineering and Testing', 'CoverMeta'),
        Spacer(1, 19), p('Project under test', 'Kicker'),
        htmlp('<link href="https://forevermart.vercel.app/" color="#B92F3B">https://forevermart.vercel.app/</link>', 'CoverMeta'),
        Spacer(1, 26), p('Audit date: 9 October 2026', 'CoverMeta'),
        p('Document revision: 10 October 2026 | Version 2.1', 'CoverMeta'),
    ], 'CoverTitle')
    section('contents', 'Table of contents', [Contents(page_map or {}, end_map or {})], separate=True)

    # Page three begins the complete confirmed-bug table, at a readable size.
    for classification, records, key_prefix, title in [
        ('Defect', D, 'bugs', 'Complete bug register'),
        ('Observation', O, 'observations', 'Observation register')]:
        rows = [['ID', 'Bug / finding', 'Severity', 'Details']]
        for record in records:
            detail = (page_map or {}).get(record['id'], '-')
            rows.append([record['id'], record['title'], record['severity'], str(detail)])
        t = table(rows, [62, 316, 76, 62], size='RegisterCell')
        section(key_prefix, title, [t], separate=classification == 'Defect')
        groups.append((title, key_prefix, key_prefix))

    for number, key in [(1, 'summary'), (3, 'scope'), (4, 'approach')]:
        title, items = extract_section(number)
        section(key, title, items, separate=key == 'summary')
        groups.append((title, key, key))
    section('reading', 'How to read the report', [
        h2('Detailed records'), p('Each record identifies the finding, test reference, affected module, URL, method, severity, priority, preconditions, reproduction steps, expected and actual result, impact, remedy, retest acceptance and evidence.'),
        h2('Defects and observations'), p('The bug register contains 70 confirmed defects. The observation register contains 20 additional quality gaps needing an owner decision. The 90 detailed records preserve their original FM identifiers; observations are excluded from the confirmed defect count.'),
        h2('Status and ownership'), p('Open means a defect is reported without a verified repair. Review required means an observation needs a product decision. Proposed owner roles have not been assigned to named people. Developer and client comments remain Not supplied.'),
        h2('Classification discipline'), p('Repeated symptoms of a shared implementation are grouped where appropriate. Separate server rules for quantity, product identity, variants, price and total retain separate records because each needs its own validation and regression assertion.'),
        h2('Evidence and corrective action'), p('Evidence paths refer to the original captures and sanitised responses in the audit folder. Recommended remedies and retest criteria describe the next corrective work; no record is claimed to be fixed or closed.'),
    ])
    groups.append(('How to read the report', 'reading', 'reading'))

    for record in R:
        meta = table([
            ['Module', record['module'], 'Severity / priority', record['severity']+' / '+record['priority']],
            ['Test reference', record['test_id'], 'Status', record['status']],
            ['Detected', '9 October 2026', 'Proposed owner', record['proposed_owner']],
        ], [82, 169, 110, 155], header=False)
        meta.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
        items = [p(record['classification'].upper()+' | '+record['category'], 'Kicker'), meta, Spacer(1,5),
                 label('Location', record['url']), label('Method', record['method']),
                 label('Preconditions', record['preconditions']), p('Reproduction procedure', 'FindingSection')]
        items += [p(f'{i}. {step}', 'FindingBody') for i, step in enumerate(record['steps'], 1)]
        items += [table([['Expected result', 'Actual result'], [record['expected'], record['actual']]], [258,258]),
                  Spacer(1, 7), label('Impact', record['impact']), p('Recommended remedy', 'FindingSection'),
                  p(record['remedy'], 'FindingBody'), p('Retest acceptance', 'FindingSection'),
                  p(record['retest'], 'FindingBody'), p('Evidence', 'FindingSection'),
                  p('; '.join(record['evidence']), 'SmallReport')]
        if record['note']:
            items.append(label('Audit note', record['note'], 'SmallReport'))
        section(record['id'], record['id']+' | '+record['title'], items, 'FindingTitle')
    groups.append(('Detailed bug and observation records', R[0]['id'], R[-1]['id']))

    for number, key in [(5,'traceability'), (6,'decision'), (7,'purchase'), (8,'severity'),
                        (9,'pareto'), (10,'modules'), (11,'status'), (12,'causes'),
                        (13,'lifecycle'), (14,'pdca'), (15,'regression')]:
        title, items = extract_section(number)
        # Introduce a large chart with its existing explanation or table so the
        # preceding page can use the space before the indivisible figure.
        if number in (9, 10, 12):
            intro = next((i for i,item in enumerate(items)
                          if isinstance(item, Paragraph) and item.style.name == 'BodyReport'), None)
            if intro is not None:
                items.insert(0, items.pop(intro))
        elif number in (11, 13, 14):
            intro = next(i for i,item in enumerate(items) if isinstance(item, Table))
            items.insert(0, items.pop(intro))
        section(key, title, items)
        groups.append((title, key, key))

    screenshots = [
        ('Hero action and spelling', 'shop-now-no-action.jpg', 'FM-001 / FM-067', 'SHOP NOW did not navigate. The hero also misspells Arrivals.'),
        ('Product identity', 'product-details.jpg', 'FM-008', 'The inspected garment image and product identity do not agree.'),
        ('Cart product names', 'cart-one-item.jpg', 'FM-020', 'Cart row displays image and money while omitting the product name.'),
        ('Empty-cart checkout', 'cart-empty.jpg', 'FM-022 / FM-023', 'An empty cart exposes checkout and inconsistent shipping/total presentation.'),
        ('Invalid delivery values', 'checkout-invalid-values.jpg', 'FM-024 / FM-025 / FM-026', 'The authorised demo COD test submitted whitespace strings and negative contact values.'),
        ('Incorrect jacket description', 'second-product-loaded.jpg', 'FM-006', 'The jacket page describes a short-sleeved shirt.'),
        ('Unknown product', 'missing-product.jpg', 'FM-011', 'A missing product leaves an incomplete purchase page.'),
        ('Unknown route', 'unknown-route.jpg', 'FM-039', 'An unrecognised route offers no explanation or recovery body.'),
    ]
    image_dir = QA/'image-excerpts'
    image_dir.mkdir(exist_ok=True)
    crop_heights = [540,610,535,535,565,590,555,495]
    for i, (title, filename, ids, description) in enumerate(screenshots, 1):
        im = PILImage.open(OUT/'evidence'/filename)
        w, h = im.size
        im = im.crop((0,0,w,min(h,crop_heights[i-1])))
        excerpt = image_dir/filename
        im.save(excerpt, quality=95)
        w, h = im.size
        image_height = min(530, 480*h/w)
        image_width = image_height*w/h
        section(f'evidence-{i}', 'Screenshot evidence | '+title,
                [p(ids, 'Kicker'), p(description),
                 Image(str(excerpt), width=image_width, height=image_height, hAlign='CENTER'),
                 Spacer(1, 5), caption('Excerpt from evidence/'+filename+'. The unmodified full capture is retained in the evidence folder.')],
                'EvidenceTitle')
    mobile_images = []
    for filename, crop_height in [('checkout-320-verified.jpg',740), ('mobile-menu-open.jpg',844)]:
        im = PILImage.open(OUT/'evidence'/filename)
        w, h = im.size
        im = im.crop((0,0,w,min(h,crop_height)))
        excerpt = image_dir/filename
        im.save(excerpt, quality=95)
        w, h = im.size
        image_height = min(440, 215*h/w)
        mobile_images.append(Image(str(excerpt), width=image_height*w/h, height=image_height))
    paired = Table([mobile_images], colWidths=[258,258])
    mobile_items = [
        p('FM-048 to FM-051 / FM-060 / FM-066', 'Kicker'), paired, Spacer(1, 10),
        table([['Measurement','Recorded result'], ['320 px checkout','Document width 352 px: horizontal overflow'],
               ['Muted home-page text','16 CSS px; contrast 2.60:1 on white (normal-text criterion 4.5:1)']], [194,322]),
        caption('Left: checkout-320-verified.jpg. Right: mobile-menu-open.jpg. Contrast uses recorded computed styles and a saved colour conversion.')]
    groups.append(('Screenshot evidence', 'evidence-1', 'evidence-8'))

    for number, key in [(22, 'api'), (23, 'book')]:
        title, items = extract_section(number)
        section(key, title, items)
        groups.append((title, key, key))
    section('evidence-mobile', 'Screenshot evidence | Mobile and accessibility', mobile_items, 'EvidenceTitle')
    groups.append(('Mobile and accessibility evidence', 'evidence-mobile', 'evidence-mobile'))
    # Keep the supporting links and handover content together before the final table.
    title, items = extract_section(24)
    for item in items:
        if isinstance(item, Table):
            for row in item._cellvalues:
                if isinstance(row[0], Paragraph) and row[0].getPlainText() == 'ForeverMart_Quality_Assurance_Report.pdf':
                    row[0] = p(FINAL.name, 'CellReport')
                if isinstance(row[0], Paragraph) and row[0].getPlainText() == 'manifest.json':
                    row[0] = p('manifest.json; compact-page-map.json', 'CellReport')
                    row[1] = p('Evidence hashes and original counts; updated report navigation map', 'CellReport')
    links = [htmlp(f'<link href="{url}" color="#B92F3B">{escape(title)}</link>', 'SmallReport') for title,url in env['refs']]
    insert = next(i for i, item in enumerate(items) if isinstance(item, Paragraph) and item.getPlainText() == 'Next review')
    items[insert:insert] = links
    section('handover', title, items)
    groups.append(('Handover and supporting references', 'handover', 'handover'))
    section('references', 'Techniques, tools and reference sources', [reference_table()], separate=True)
    groups.append(('Techniques, tools and reference sources', 'references', 'references'))
    TOC_GROUPS = groups
    return story

first = AuditDoc(QA/'pagination-pass.pdf')
first.build(make_story())
second = AuditDoc(FINAL)
second.build(make_story(first.section_pages, first.section_ends))
assert second.section_pages == first.section_pages, 'Pagination changed after resolving contents references'
assert second.section_ends == first.section_ends, 'Section ends changed after resolving references'
assert second.section_pages['cover'] == 1
assert second.section_pages['contents'] == 2
assert second.section_pages['bugs'] == 3

reader = PdfReader(FINAL)
page_count = len(reader.pages)
sections = second.section_order
spans = {}
for i, (key, start, title) in enumerate(sections):
    end = second.section_ends[key]
    spans[key] = dict(start=start, end=end, title=title)
assert spans['cover']['end'] == 1 and spans['contents']['end'] == 2
assert spans['references']['start'] == page_count
for record in R:
    span = spans[record['id']]
    assert span['end'] >= span['start'], f'Invalid record range: {record["id"]}'
    text = '\n'.join(page.extract_text() for page in reader.pages[span['start']-1:span['end']])
    for field in ['Reproduction procedure','Expected result','Actual result','Impact',
                  'Recommended remedy','Retest acceptance','Evidence']:
        assert field in text, (record['id'], field)
    assert ' '.join(clean(record['title']).split()) in ' '.join(text.split()), record['id']

all_text = '\n'.join(page.extract_text() for page in reader.pages)
assert 'Ghulam Mohiuddin' in reader.pages[0].extract_text()
assert 'B22110106023' in reader.pages[0].extract_text()
assert 'Supported defects' not in reader.pages[0].extract_text()
assert 'Reading guide' not in reader.pages[1].extract_text()
assert 'Complete bug register' in reader.pages[2].extract_text()
assert 'Test method' in reader.pages[-1].extract_text()
assert 'Report tools' in reader.pages[-1].extract_text()

problems = []
with pdfplumber.open(FINAL) as pdf:
    for number, page in enumerate(pdf.pages, 1):
        words = page.extract_words()
        for word in words:
            if word['x0'] < 35 or word['x1'] > PW-33:
                problems.append(f'Page {number}: text outside horizontal margins: {word["text"]}')
            if PH-50 < word['top'] < PH-39:
                problems.append(f'Page {number}: content intrudes into footer: {word["text"]}')
    body_sizes = sorted(set(round(c['size'],1) for page in pdf.pages[3:] for c in page.chars))
assert not problems, '\n'.join(problems[:15])

rendered = pdfium.PdfDocument(str(FINAL))
for index in range(page_count):
    rendered[index].render(scale=1.15).to_pil().save(QA/f'page-{index+1:03d}.png')
for start in range(0, page_count, 4):
    sheet = PILImage.new('RGB', (1440, 2090), '#D8DCE1')
    draw = ImageDraw.Draw(sheet)
    for offset in range(4):
        index = start+offset
        if index >= page_count:
            break
        im = PILImage.open(QA/f'page-{index+1:03d}.png').convert('RGB')
        im.thumbnail((700,995))
        x = 10+(offset%2)*720
        y = 35+(offset//2)*1045
        sheet.paste(im, (x,y))
        draw.text((x,y-23), f'Page {index+1}', fill='#252830')
    sheet.save(QA/f'sheet-{start//4+1:02d}.jpg', quality=88)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
checks = dict(pages=page_count, previous_pages=128, pages_removed=128-page_count,
              title_page=1, contents_page=2, bug_register_start=3,
              bug_register_pages=[spans['bugs']['start'],spans['bugs']['end']],
              observation_register_pages=[spans['observations']['start'],spans['observations']['end']],
              final_reference_table_page=page_count, confirmed_defects=70, observations=20,
              main_font_pt=12, record_font_pt=11.8, table_font_pt=10.6,
              register_font_pt=11.2, contents_font_pt=12, rendered_pages=page_count,
              source_preserved=True, problems=problems, body_font_sizes=body_sizes)
(OUT/'compact-page-map.json').write_text(json.dumps(spans, indent=2), encoding='utf-8')
(OUT/'compact-layout-verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
print('Section spans:', {k: (v['start'],v['end']) for k,v in spans.items() if not k.startswith('FM-')})
