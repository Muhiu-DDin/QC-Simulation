"""Create a designed cover while preserving the compact audit and PDF links."""
from pathlib import Path
import hashlib
import json

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_Compact.pdf'
if not SOURCE.exists():
    SOURCE = ROOT.parent / 'ForeverMart_Quality_Assurance_Report_Compact.pdf'
FINAL = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_Final.pdf'
QA = ROOT / 'tmp/pdfs/forevermart-final-cover'
QA.mkdir(parents=True, exist_ok=True)
COVER = QA / 'cover.pdf'
PW, PH = A4
INK = HexColor('#252830')
RED = HexColor('#B92F3B')
MUTED = HexColor('#657080')
LINE = HexColor('#D8DCE2')
FN, FB = 'CoverArial', 'CoverArialBold'
pdfmetrics.registerFont(TTFont(FN, 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont(FB, 'C:/Windows/Fonts/arialbd.ttf'))


def tracked(c, text, x, y, size=9, spacing=1.5, color=MUTED, font=FB):
    obj = c.beginText(x, y)
    obj.setFont(font, size)
    obj.setCharSpace(spacing)
    obj.setFillColor(color)
    obj.textOut(text)
    c.drawText(obj)


def text(c, value, x, y, size=12, font=FN, color=INK):
    obj = c.beginText(x, y)
    obj.setFont(font, size)
    obj.setFillColor(color)
    obj.setCharSpace(0)
    obj.textOut(value)
    c.drawText(obj)


def make_cover():
    c = canvas.Canvas(str(COVER), pagesize=A4)
    c.setTitle('ForeverMart | Software Quality Assurance Report')
    c.setAuthor('Ghulam Mohiuddin')
    c.setFillColor(white)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    # A strong editorial title panel with restrained vector geometry.
    hero_bottom = 373
    c.setFillColor(INK)
    c.rect(0, hero_bottom, PW, PH - hero_bottom, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, hero_bottom, 12, PH - hero_bottom, fill=1, stroke=0)
    tracked(c, 'SOFTWARE TESTING', 48, PH - 55, color=white)
    tracked(c, 'PART 03 / 2026', 405, PH - 55, size=8.5,
            spacing=1.15, color=HexColor('#CED2D9'))
    c.setStrokeColor(HexColor('#484C55'))
    c.setLineWidth(.6)
    c.line(48, PH - 76, PW - 48, PH - 76)
    tracked(c, 'PORTFOLIO REPORT', 48, 720, size=10,
            spacing=2, color=HexColor('#E79AA2'))
    text(c, 'ForeverMart', 46, 662, size=47, font=FB, color=white)
    text(c, 'Software Quality', 48, 607, size=31, font=FB, color=white)
    text(c, 'Assurance Report', 48, 567, size=31, font=FB, color=white)
    c.setFillColor(RED)
    c.rect(48, 536, 66, 4, fill=1, stroke=0)
    text(c, 'Defect documentation', 48, 505, size=13.5,
         color=HexColor('#D4D7DE'))
    text(c, 'and corrective actions', 48, 485, size=13.5,
         color=HexColor('#D4D7DE'))
    # Abstract layered squares give the cover depth without distracting
    # from the report title or implying untested audit results.
    c.saveState()
    c.translate(477, 436)
    c.rotate(45)
    c.setStrokeColor(HexColor('#444851'))
    c.setLineWidth(.85)
    for extent in (52, 80, 108):
        c.rect(-extent / 2, -extent / 2, extent, extent, fill=0, stroke=1)
    c.setStrokeColor(RED)
    c.setLineWidth(3)
    c.line(-40, -40, 40, -40)
    c.line(40, -40, 40, 40)
    c.restoreState()
    c.setFillColor(RED)
    c.rect(48, hero_bottom - 5, 192, 10, fill=1, stroke=0)

    tracked(c, 'SUBMITTED BY', 48, 333, size=9, spacing=1.3)
    text(c, 'Ghulam Mohiuddin', 48, 303, size=21, font=FB)
    text(c, 'Seat number', 48, 279, size=11, color=MUTED)
    text(c, 'B22110106023', 122, 279, size=12, font=FB)
    c.setStrokeColor(LINE)
    c.setLineWidth(.65)
    c.line(48, 255, PW - 48, 255)

    tracked(c, 'COURSE', 48, 232, size=9, spacing=1.3)
    text(c, 'Software Quality Engineering and Testing', 48, 211,
         size=12.5, font=FB)
    tracked(c, 'PROJECT UNDER TEST', 48, 179, size=9, spacing=1.3)
    text(c, 'https://forevermart.vercel.app/', 48, 158,
         size=12.5, color=RED)
    c.linkURL('https://forevermart.vercel.app/',
              (48, 154, 48 + pdfmetrics.stringWidth(
                  'https://forevermart.vercel.app/', FN, 12.5), 173),
              relative=0, thickness=0)
    c.line(48, 136, PW - 48, 136)
    tracked(c, 'AUDIT DATE', 48, 112, size=8.5, spacing=1.1)
    tracked(c, 'DOCUMENT REVISION', 305, 112, size=8.5, spacing=1.1)
    text(c, '9 October 2026', 48, 91, size=12, font=FB)
    text(c, '10 October 2026 / Version 2.2', 305, 91, size=11.5, font=FB)

    c.setFillColor(RED)
    c.rect(0, 0, PW, 9, fill=1, stroke=0)
    text(c, 'Software Testing  /  Portfolio Part 3', 48, 34, size=9,
         color=MUTED)
    text(c, '01', PW - 63, 34, size=10, font=FB, color=RED)
    c.showPage()
    c.save()


def destination_pages(reader):
    destinations = []
    for page in reader.pages:
        for ref in page.get('/Annots', []):
            annot = ref.get_object()
            dest = annot.get('/Dest')
            if dest and isinstance(dest, list):
                target = dest[0]
                number = next((i for i, p in enumerate(reader.pages)
                               if p.indirect_reference == target), None)
                destinations.append(number)
    return destinations


def run():
    before_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    make_cover()
    original = PdfReader(SOURCE)
    cover = PdfReader(COVER)
    writer = PdfWriter()
    writer.clone_document_from_reader(original)
    first = writer.pages[0]
    new = cover.pages[0]
    # Replace only the cover's presentation. Keeping the page object preserves
    # all internal links, outlines and the existing 95-page pagination.
    for key in ('/Contents', '/Resources', '/MediaBox', '/CropBox', '/Annots'):
        name = NameObject(key)
        if name in new:
            first[name] = new.raw_get(name).clone(writer)
        elif name in first:
            del first[name]
    writer.add_metadata({
        '/Title': 'ForeverMart | Software Quality Assurance Report',
        '/Author': 'Ghulam Mohiuddin',
        '/Subject': 'Software Testing Portfolio Part 3',
    })
    with FINAL.open('wb') as stream:
        writer.write(stream)

    final = PdfReader(FINAL)
    assert len(final.pages) == len(original.pages) == 95
    assert all(final.pages[i].extract_text() == original.pages[i].extract_text()
               for i in range(1, len(final.pages)))
    assert destination_pages(final) == destination_pages(original)
    assert len(final.outline) == len(original.outline)
    for value in ('Ghulam Mohiuddin', 'B22110106023', 'ForeverMart',
                  '9 October 2026', '10 October 2026'):
        assert value in final.pages[0].extract_text()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before_hash

    doc = pdfium.PdfDocument(str(FINAL))
    old = pdfium.PdfDocument(str(SOURCE))
    cover_render = doc[0].render(scale=1.7).to_pil()
    designed_render = pdfium.PdfDocument(str(COVER))[0].render(scale=1.7).to_pil()
    assert cover_render.size == designed_render.size
    assert cover_render.tobytes() == designed_render.tobytes()
    cover_render.save(QA / 'title-page.png')
    # Confirm every unchanged page also renders identically, including links
    # and charts carried across by the PDF object clone.
    for i in range(1, len(doc)):
        actual = doc[i].render(scale=.7).to_pil()
        expected = old[i].render(scale=.7).to_pil()
        assert actual.size == expected.size
        assert actual.tobytes() == expected.tobytes(), f'Changed page {i + 1}'
    report = {'pages': len(final.pages), 'cover_updated': True,
              'unchanged_pages': 94, 'unchanged_page_text': True,
              'unchanged_page_renders': True,
              'internal_link_targets_preserved': True,
              'outlines_preserved': True, 'source_unchanged': True}
    (QA / 'verification.json').write_text(json.dumps(report, indent=2),
                                          encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    run()
