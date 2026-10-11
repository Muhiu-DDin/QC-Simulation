"""Publish the confirmed-defect edition: one detailed defect per page.

The original audit and evidence stay unchanged. Additional quality context and
follow-up checks are editorial analysis and proposed tests, not new test results.
"""
from pathlib import Path
import ast
import json
import re
import hashlib
from collections import Counter
from html import escape
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
# Load the reusable layout helpers without running the old report build.
layout_source = (ROOT / 'tools/compact_forevermart_report.py').read_text(encoding='utf-8')
helpers = layout_source.split('def make_story(')[0]
helpers = helpers.replace("QA = ROOT / 'tmp/pdfs/forevermart-compact'",
                          "QA = ROOT / 'tmp/pdfs/forevermart-confirmed'")
helpers = helpers.replace("FINAL = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_Compact.pdf'",
                          "FINAL = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_70_Defects.pdf'")
helpers = helpers.replace("SOURCE = Path('C:/Users/Muhiddin/OneDrive/Desktop/ForeverMart_Quality_Assurance_Report_With_Contents.pdf')",
                          "SOURCE = ROOT / 'output/pdf/ForeverMart_Quality_Assurance_Report_Final.pdf'")
helpers = helpers.replace("assert len(D) == 70 and len(O) == 20",
                          "assert len(D) == 70 and len(O) == 20\nREMOVED_IDS = {r['id'] for r in O}\nR = D\nO = []")
exec(compile(helpers, '<reusable audit layout>', 'exec'), globals())

from pypdf import PdfWriter
from pypdf.generic import NameObject
from forevermart_record_context import CONTEXT

# A zero-height navigation marker must not be pushed onto a fresh page by
# the preceding paragraph's trailing space. Its bookkeeping happens in
# afterFlowable; frameAction makes it independent of remaining frame height.
SectionEnd.frameAction = lambda self, frame: None

# Edit the source *text* used to construct reusable analysis sections. No old
# builder is imported and no earlier report, registry or evidence is rewritten.
old_source = (ROOT / 'tools/build_forevermart_report.py').read_text(encoding='utf-8')
edits = {
    'Product choices and hardening recommendations are labelled observations where acceptance requires owner review.':
        'This edition presents only confirmed failures against those criteria.',
    ",\n           ['AC-10 Product-owner review','FM-003, 071-078, 080-090','Decide and approve observations before treating them as defects']": '',
    'The 20 observations are excluded.': 'All 70 records are confirmed defects.',
    'Confirm requirements, review observations and accept any residual risk':
        'Confirm defect criteria, assign corrective work and accept any residual risk',
    'Reviewed criteria and an owner decision for each observation':
        'Reviewed acceptance criteria and agreed defect priorities',
    'finally review the optional hardening and optimisation observations.':
        'then run the agreed regression checks before closure.',
    "['Public content and configuration','FM-067-090 as applicable','Proofread pages; verify approved contacts/policies; check headers and metadata']":
        "['Public content','FM-067-070, FM-079','Proofread affected pages; reconcile approved contact details across routes']",
}
for old, new in edits.items():
    assert old in old_source, old
    old_source = old_source.replace(old, new)
old_tree = ast.parse(old_source)


class DefectSheet(Flowable):
    """An indivisible, measured sheet that fills one A4 content frame."""
    def __init__(self, record, ordinal):
        super().__init__()
        self.record = record
        self.ordinal = ordinal
        self.section_key = record['id']
        self.section_title = record['id'] + ' | ' + record['title']
        self.width = WIDTH
        self.height = PH - TOP - BOTTOM
        self.blocks, self.metrics = self.compose()

    def compose(self):
        r = self.record
        context = CONTEXT[r['id']]
        # Keep the original evidence and assertions verbatim. Use the largest
        # readable size that fits, with relevant context taking priority over
        # optional explanatory repetition.
        def make(size, include_rationale, include_checks, include_closure=False):
            body = ParagraphStyle('SheetBody', fontName=FN, fontSize=size,
                                  leading=size*1.25, textColor=INK)
            small = ParagraphStyle('SheetSmall', parent=body, fontSize=10,
                                   leading=12.3, textColor=GRAY)
            head = ParagraphStyle('SheetHead', fontName=FB, fontSize=11.2,
                                  leading=14, textColor=INK)
            title = ParagraphStyle('SheetTitle', fontName=FB, fontSize=20,
                                   leading=24, textColor=INK)
            def para(value, style=body):
                return Paragraph(escape(clean(value)), style)
            def inline(label, value, style=body):
                return Paragraph('<b>'+escape(label)+'</b> '+escape(clean(value)), style)
            blocks = [(para(r['title'], title), 10)]
            meta = table([
                ['Module', r['module'], 'Severity / priority', r['severity']+' / '+r['priority']],
                ['Test ID', r['test_id'], 'Status / owner', 'Open / '+r['proposed_owner']],
            ], [67, 177, 108, 164], header=False)
            meta.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),4),
                                      ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            blocks += [(meta, 8), (inline('Location:',r['url'],small),3),
                       (inline('Method:',r['method'],small),3),
                       (inline('Preconditions:',r['preconditions']),7),
                       (para('Reproduction procedure',head),4)]
            for index, step in enumerate(r['steps'],1):
                blocks.append((para(f'{index}. {step}'),3))
            result_styles = [ParagraphStyle('ResultHead',parent=head,textColor=colors.white), body]
            cells = [[Paragraph('Expected result',result_styles[0]),
                      Paragraph('Actual result',result_styles[0])],
                     [para(r['expected']),para(r['actual'])]]
            comparison = Table(cells,colWidths=[258,258],hAlign='LEFT')
            comparison.setStyle(TableStyle([
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BACKGROUND',(0,0),(-1,0),INK),
                ('BACKGROUND',(0,1),(-1,1),PALE),
                ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LINEBELOW',(0,1),(-1,1),.4,BORDER)]))
            blocks += [(comparison,9), (para('Impact and quality context',head),4),
                       (para(r['impact']+' '+context['quality_context']),8),
                       (para('Recommended remedy',head),4), (para(r['remedy']),4)]
            if include_rationale:
                blocks.append((para(context['fix_rationale']),7))
            blocks += [(para('Retest acceptance',head),4), (para(r['retest']),4)]
            if include_checks:
                blocks.append((inline('Additional regression checks (proposed):',
                                      context['additional_checks']),7))
            if include_closure:
                if r['module']=='Account API':
                    closure=('Capture a sanitized list of own-profile response field names from the identified fix build, excluding secret values. Demonstrate that password and refresh-token fields are absent while approved profile fields and authorised account functions remain available. Inspect related login responses as specified by the acceptance criteria.')
                elif r['category']=='Data integrity' and r['module']=='Checkout':
                    closure=('Capture the form input, rejection feedback and sanitized own-order read-back in the identified fix build. Demonstrate that invalid delivery data or an empty item list creates no order. Repeat a valid COD purchase and compare its saved delivery data with the accepted form values.')
                elif 'API' in r['method'] or r['module'] in ('Order API','Cart API'):
                    closure=('Capture sanitized request/response pairs and read-back for valid and rejected inputs in the identified fix build. A successful response alone is insufficient: demonstrate that invalid data was not persisted and that the related valid operation still works.')
                elif r['category']=='Accessibility':
                    closure=('Retain a fresh DOM or computed-style extract together with a screenshot of the affected control in the fix build. Demonstrate the stated acceptance check with the relevant keyboard, label, contrast or reflow evidence; a visual style change alone does not establish accessibility.')
                elif r['category']=='Content':
                    closure=('Attach the approved copy or product-data source and a new capture of the affected page after repair. Compare the visible text with that source, then repeat the stated acceptance check in the identified fix build. Confirm the rendered result rather than relying only on an edited source file.')
                else:
                    closure=('Capture the affected page before and after the same action in the identified fix build. Record the URL or state transition, then repeat the stated acceptance and additional regression checks. A changed appearance alone should not be treated as proof that the action is working.')
                blocks += [(para('Evidence to collect at retest (proposed)',head),4),
                           (para(closure),8)]
            blocks += [(inline('Evidence:', '; '.join(r['evidence']),small),3)]
            if r['note']:
                blocks.append((inline('Audit note:',r['note'],small),3))
            blocks.append((para('Detected 9 October 2026. No fix build or closure evidence. '
                                'Owner role proposed; developer/client comments not supplied.',small),0))
            sizes = [(item.wrap(WIDTH, self.height)[1], gap) for item,gap in blocks]
            return blocks, sizes, sum(h+gap for h,gap in sizes)

        available = self.height - 33
        # 11.4 pt is the minimum body size; no content scaling is applied.
        choices = [(11.7,True,True,True),(11.7,True,True,False),
                   (11.7,False,True,False),(11.7,False,False,False),
                   (11.4,True,True,False),(11.4,False,True,False),(11.4,False,False,False)]
        for size, rationale, checks, closure in choices:
            blocks, dimensions, used = make(size,rationale,checks,closure)
            if used <= available:
                remaining = available - used
                # Distribute spare height between substantive sections. Avoid
                # a large blank tail, excessive word spacing or filler text.
                candidates = [i for i,(item,gap) in enumerate(blocks)
                              if gap >= 7]
                extra = min(remaining/len(candidates),13) if candidates else 0
                placed = []
                for i, ((item,gap),(height,_)) in enumerate(zip(blocks,dimensions)):
                    placed.append((item,height,gap+(extra if i in candidates else 0)))
                stats = dict(body_font_pt=size,quality_context=True,
                             fix_rationale=rationale,proposed_extra_checks=checks,
                             proposed_closure_evidence=closure,
                             content_height_pt=round(used+extra*len(candidates),1),
                             unused_bottom_pt=round(remaining-extra*len(candidates),1))
                return placed,stats
        raise ValueError(f'{r["id"]}: cannot fit the complete defect on one readable page')

    def draw(self):
        c=self.canv
        c.setFont(FB,10.5)
        c.setFillColor(RED)
        c.drawString(0,self.height-12,self.record['id']+' / CONFIRMED DEFECT')
        c.setFont(FN,10)
        c.setFillColor(GRAY)
        c.drawRightString(WIDTH,self.height-12,
                          self.record['category']+' | '+str(self.ordinal)+' of 70')
        y=self.height-33
        for item,height,gap in self.blocks:
            item.drawOn(c,0,y-height)
            y-=height+gap
        assert y >= -0.1, (self.section_key,y)


class ConfirmedDoc(AuditDoc):
    def afterFlowable(self,item):
        if isinstance(item,DefectSheet):
            self.active_section=item.section_key
            self.section_pages[item.section_key]=self.page
            self.section_ends[item.section_key]=self.page
            self.section_order.append((item.section_key,self.page,item.section_title))
            self.canv.bookmarkHorizontalAbsolute(item.section_key,PH-TOP)
            self.canv.addOutlineEntry(item.section_title,item.section_key,level=0)
            self.page_start_section=item.section_key
            self.page_starts_with_continuation=False
        else:
            super().afterFlowable(item)


def summary_items():
    return [
        p('ForeverMart supports basic catalogue browsing, size selection, cart use and cash-on-delivery ordering. The confirmed defects concern server validation and pricing, customer-state loss, incomplete storefront actions, inaccurate product content and accessibility barriers.'),
        table([['Result','Count','Interpretation'],
               ['Confirmed defects','70','Reproduced behaviour or inspected implementation conflicts with the stated audit criterion.'],
               ['High / Medium / Low','13 / 48 / 9','Priorities P1 / P2 / P3 are proposed corrective order.'],
               ['Verified fixed or closed','0','No repaired build or successful closure retest has been supplied.'],
               ['Original assignment target','100','70 distinct defects are documented; the remaining 30 were not established.']], [143,91,282]),
        h2('Immediate corrective priorities'),
        p('Repair authoritative server price/total calculation and reject invalid item lists, product identities, variants, quantities and delivery values. Resolve the profile response exposing authentication-related fields. Preserve customer cart and checkout state through authentication.'),
        h2('Release recommendation'),
        p('Hold real customer ordering until High-severity defects are corrected and independently retested. Then repair shared storefront actions, accessibility and product copy, running the related regression checks before closure.'),
        h2('Evidence and limits'),
        p('The audit used screenshots, DOM snapshots, public catalogue data and client JavaScript, plus authorised API requests and read-back for one disposable account. No administrator operations, real card settlement, server source, load tests or other-user records were tested.'),
        caption('Original audit: 9 October 2026. This edition contains confirmed defects only. Summary adapted from Lewis E11 and E29; added explanations and follow-up checks are analysis and proposed work, not new executions.')]


def status_items():
    return [env['bars']({'Open defects':70,'Verified closed':0},'Confirmed-defect status',height=170),
            caption('Status is based on the 70 confirmed records in this report. No repair or closure evidence has been received.'),
            table([['Metric','Value or limitation'],['Confirmed defect count','70'],
                   ['Open / closed','70 / 0'],['Assignment target shortfall','30 confirmed records'],
                   ['Defect density','Not calculated: no valid source-size denominator.'],
                   ['Test coverage percentage','Not calculated: no complete requirements/test denominator.'],
                   ['Defect age / closure trend','Not calculated: no repair history or closure dates.'],
                   ['Performance / load curves','Not measured in the authorised audit.']], [205,311]),
            caption('Lewis Chapter 24 describes age, density and tracking curves. Those measurements require data unavailable for this audit; no time series or source-size figures are invented.')]


def confirmed_reference_table():
    result=reference_table()
    # CSP/header recommendations belonged to the removed records and are not
    # an active reference for this confirmed-defect edition.
    for row in result._cellvalues:
        if isinstance(row[1],Paragraph) and row[1].getPlainText()=='OWASP REST Security; MDN CSP':
            row[1]=p('OWASP REST Security Cheat Sheet','CellReport')
            row[2]=p('Server validation, trusted pricing and response-data exposure remedies. See the supporting references.','CellReport')
    return result


SHEET_METRICS={}
def make_story(page_map=None,end_map=None):
    global TOC_GROUPS
    story=[]
    groups=[]
    def section(key,title,items,style_name='H1Report',separate=False):
        if story and separate:
            story.append(PageBreak())
        heading=Heading(title,key,style_name)
        if key.startswith('evidence-') and key!='evidence-mobile':
            story.append(KeepTogether([heading,*items,SectionEnd(key)]))
            return
        if items and isinstance(items[0],Table) and items[0]._nrows>4:
            heading.keepWithNext=False
            items[0].wrap(WIDTH,PH)
            minimum=heading.wrap(WIDTH,PH)[1]+heading.getSpaceBefore()+heading.getSpaceAfter()
            minimum+=sum(items[0]._rowHeights[:2])+2
            story.append(CondPageBreak(minimum))
        story.append(heading)
        for index,item in enumerate(items):
            if (isinstance(item,(Drawing,Image)) and index+1<len(items)
                    and isinstance(items[index+1],Paragraph)
                    and items[index+1].style.name=='SmallReport'):
                object.__setattr__(item,'keepWithNext',True)
            story.append(item)
        story.append(SectionEnd(key))

    # Replaced after pagination with the professionally designed cover.
    section('cover','ForeverMart',[Spacer(1,500)],'CoverTitle')
    section('contents','Table of contents',[Contents(page_map or {},end_map or {})],separate=True)
    rows=[['ID','Confirmed defect','Severity','Details']]
    for record in D:
        rows.append([record['id'],record['title'],record['severity'],str((page_map or {}).get(record['id'],'-'))])
    section('bugs','Complete bug register',[table(rows,[62,316,76,62],size='RegisterCell')],separate=True)
    groups.append(('Complete bug register','bugs','bugs'))
    section('summary','Executive summary',summary_items(),separate=True)
    groups.append(('Executive summary','summary','summary'))
    for number,key in [(3,'scope'),(4,'approach')]:
        title,items=extract_section(number)
        section(key,title,items)
        groups.append((title,key,key))
    section('reading','How to read the defect sheets',[
        h2('One defect per page'),
        p('Each of the 70 detailed sheets starts on a new page and stays on that page. It records the affected module, test reference, location, method, preconditions, reproduction procedure, expected/actual result, impact, remedy, retest acceptance and evidence.'),
        h2('Stable identifiers'),
        p('Original FM and TC identifiers are retained so they still match the captured evidence. Numbering gaps are intentional; this report contains 70 confirmed defects, not a sequence of 79 new findings.'),
        h2('Added explanation and retests'),
        p('Quality context explains the recorded impact and why the proposed remedy is appropriate. Additional regression checks are explicitly proposed; they have not been executed. The sheets do not claim a server root cause that the available evidence cannot prove.'),
        h2('Status and ownership'),
        p('Every defect is Open. Owner roles are proposed and not assigned to named people. No corrected build or closure evidence has been provided. Fix implementation and acceptance testing remain the next steps.')])
    groups.append(('How to read the defect sheets','reading','reading'))

    for ordinal,record in enumerate(D,1):
        story.append(PageBreak())
        sheet=DefectSheet(record,ordinal)
        SHEET_METRICS[record['id']]=sheet.metrics
        story.append(sheet)
    groups.append(('Detailed confirmed defects (70 sheets)',D[0]['id'],D[-1]['id']))

    for number,key in [(5,'traceability'),(6,'decision'),(7,'purchase'),(8,'severity'),
                       (9,'pareto'),(10,'modules'),(11,'status'),(12,'causes'),
                       (13,'lifecycle'),(14,'pdca'),(15,'regression')]:
        title,items=extract_section(number) if number!=11 else ('Status and measurement boundaries',status_items())
        section(key,title,items,separate=number==5)
        groups.append((title,key,key))

    screenshots=[
        ('Hero action and spelling','shop-now-no-action.jpg','FM-001 / FM-067','SHOP NOW did not navigate. The hero also misspells Arrivals.',540),
        ('Product identity','product-details.jpg','FM-008','The inspected garment image and product identity do not agree.',610),
        ('Cart product names','cart-one-item.jpg','FM-020','Cart row displays image and money while omitting the product name.',535),
        ('Empty-cart checkout','cart-empty.jpg','FM-022 / FM-023','An empty cart exposes checkout and inconsistent shipping/total presentation.',535),
        ('Invalid delivery values','checkout-invalid-values.jpg','FM-024 / FM-025 / FM-026','The authorised demo COD test submitted whitespace strings and negative contact values.',565),
        ('Incorrect jacket description','second-product-loaded.jpg','FM-006','The jacket page describes a short-sleeved shirt.',590),
        ('Unknown product','missing-product.jpg','FM-011','A missing product leaves an incomplete purchase page.',555),
        ('Unknown route','unknown-route.jpg','FM-039','An unrecognised route offers no explanation or recovery body.',495)]
    image_dir=QA/'image-excerpts'
    image_dir.mkdir(exist_ok=True)
    for index,(title,filename,ids,description,crop_height) in enumerate(screenshots,1):
        im=PILImage.open(OUT/'evidence'/filename)
        w,h=im.size
        im=im.crop((0,0,w,min(h,crop_height)))
        excerpt=image_dir/filename
        im.save(excerpt,quality=95)
        w,h=im.size
        ih=min(530,480*h/w)
        section(f'evidence-{index}','Screenshot evidence | '+title,[
            p(ids,'Kicker'),p(description),Image(str(excerpt),width=ih*w/h,height=ih,hAlign='CENTER'),
            Spacer(1,5),caption('Excerpt from evidence/'+filename+'. The unmodified full capture is retained in the evidence folder.')],'EvidenceTitle')
    groups.append(('Screenshot evidence','evidence-1','evidence-8'))

    for number,key in [(22,'api'),(23,'book')]:
        title,items=extract_section(number)
        section(key,title,items)
        groups.append((title,key,key))

    mobile=[]
    for filename,crop_height in [('checkout-320-verified.jpg',740),('mobile-menu-open.jpg',844)]:
        im=PILImage.open(OUT/'evidence'/filename)
        w,h=im.size
        im=im.crop((0,0,w,min(h,crop_height)))
        excerpt=image_dir/filename
        im.save(excerpt,quality=95)
        w,h=im.size
        ih=min(440,215*h/w)
        mobile.append(Image(str(excerpt),width=ih*w/h,height=ih))
    section('evidence-mobile','Screenshot evidence | Mobile and accessibility',[
        p('FM-048 to FM-051 / FM-060 / FM-066','Kicker'),Table([mobile],colWidths=[258,258]),Spacer(1,10),
        table([['Measurement','Recorded result'],['320 px checkout','Document width 352 px: horizontal overflow'],
               ['Muted home-page text','16 CSS px; contrast 2.60:1 on white (normal-text criterion 4.5:1)']],[194,322]),
        caption('Left: checkout-320-verified.jpg. Right: mobile-menu-open.jpg. Contrast uses recorded computed styles and a saved colour conversion.')],'EvidenceTitle')
    groups.append(('Mobile and accessibility evidence','evidence-mobile','evidence-mobile'))

    refs=[(title,url) for title,url in env['refs'] if 'Content Security Policy' not in title]
    section('handover','Handover and supporting references',[
        p('This confirmed-defect edition addresses Software Testing Portfolio Part 3 for ForeverMart. It preserves the original audited failures and evidence while adding explanatory context and proposed regression checks.'),
        h2('Handover materials'),
        table([['Material','Purpose'],['This report','70 individual defect sheets, register, analysis, workflows and evidence excerpts.'],
               ['confirmed-defects.json','Filtered 70-record register plus clearly separated explanatory context.'],
               ['confirmed-page-map.json','Current section and defect page numbers.'],
               ['evidence and raw folders','Original captures and sanitized responses referenced by the sheets.']], [180,336]),
        h2('Next review'),
        p('Assign corrective owners, agree the affected acceptance criteria, repair the High-priority rules first and provide an identified fix build. Reproduce the original failure, perform the stated acceptance check and related regression, then attach fresh evidence before closing a record.'),
        h2('Supporting standards and guidance'),
        *[htmlp(f'<link href="{url}" color="#B92F3B">{escape(title)}</link>','SmallReport') for title,url in refs],
        caption('Targeted accessibility checks do not constitute complete WCAG certification. No fixes or follow-up regression checks are claimed to be completed.')])
    groups.append(('Handover and supporting references','handover','handover'))
    section('references','Techniques, tools and reference sources',[confirmed_reference_table()],separate=True)
    groups.append(('Techniques, tools and reference sources','references','references'))
    TOC_GROUPS=groups
    return story


def replace_cover():
    # Reuse the designed cover layout, updating only this edition's revision.
    cover_source=(ROOT/'tools/upgrade_forevermart_cover.py').read_text(encoding='utf-8')
    cover_source=cover_source.split('def destination_pages(')[0]
    cover_source=cover_source.replace("QA = ROOT / 'tmp/pdfs/forevermart-final-cover'",
                                      "QA = ROOT / 'tmp/pdfs/forevermart-confirmed/cover'")
    cover_source=cover_source.replace('Version 2.2','Version 3.0')
    cover_env={'__file__':str(ROOT/'tools/upgrade_forevermart_cover.py')}
    exec(compile(cover_source,'<existing designed cover>','exec'),cover_env)
    cover_env['make_cover']()
    current=PdfReader(FINAL)
    cover=PdfReader(cover_env['COVER'])
    writer=PdfWriter()
    writer.clone_document_from_reader(current)
    for key in ('/Contents','/Resources','/MediaBox','/CropBox','/Annots'):
        name=NameObject(key)
        if name in cover.pages[0]:
            writer.pages[0][name]=cover.pages[0].raw_get(name).clone(writer)
        elif name in writer.pages[0]:
            del writer.pages[0][name]
    writer.add_metadata({'/Title':'ForeverMart | Quality Assurance Report - 70 Confirmed Defects',
                         '/Author':'Ghulam Mohiuddin','/Subject':'Software Testing Portfolio Part 3'})
    with FINAL.open('wb') as stream:
        writer.write(stream)


def verify(doc):
    reader=PdfReader(FINAL)
    spans={key:dict(start=start,end=doc.section_ends[key],title=title)
           for key,start,title in doc.section_order}
    assert spans['cover']['start']==spans['cover']['end']==1
    assert spans['contents']['start']==spans['contents']['end']==2
    assert spans['bugs']['start']==3
    assert spans['references']['start']==spans['references']['end']==len(reader.pages)
    ids={r['id'] for r in D}
    for record in D:
        span=spans[record['id']]
        assert span['start']==span['end'],record['id']
        text=reader.pages[span['start']-1].extract_text()
        normalize=lambda value:re.sub(r'\s+','',clean(value)).casefold()
        norm=normalize(text)
        for key in ('title','url','method','preconditions','expected','actual','impact','remedy','retest','note'):
            assert normalize(record[key]) in norm,(record['id'],key)
        for value in record['steps']+record['evidence']:
            assert normalize(value) in norm,(record['id'],value)
        assert normalize(CONTEXT[record['id']]['quality_context']) in norm,record['id']
        for key in ('fix_rationale','additional_checks'):
            assert normalize(CONTEXT[record['id']][key]) in norm,(record['id'],key)
        assert (set(re.findall(r'FM-\d{3}',text)) & ids)=={record['id']},record['id']
    text='\n'.join(page.extract_text() for page in reader.pages)
    assert all(len(page.extract_text().strip())>150 for page in reader.pages), 'Empty content page'
    # No removed IDs, observation records, references or counts may survive.
    assert not re.search(r'observation',text,re.I),'Observation wording remains'
    assert not (set(re.findall(r'FM-\d{3}',text)) & REMOVED_IDS),'Removed record reference remains'
    assert '90 detailed' not in text and '20 additional' not in text
    defect_pages=[spans[record['id']]['start'] for record in D]
    assert defect_pages==list(range(defect_pages[0],defect_pages[0]+70))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
    # Resolve every clickable TOC target and its printed page range.
    targets=[]
    for ref in reader.pages[1].get('/Annots',[]):
        dest=ref.get_object().get('/Dest')
        if dest:
            target=next(i+1 for i,page in enumerate(reader.pages) if page.indirect_reference==dest[0])
            targets.append(target)
    assert targets==[spans[first]['start'] for _,first,_ in TOC_GROUPS]

    problems=[]
    with pdfplumber.open(FINAL) as pdf:
        for number,page in enumerate(pdf.pages[1:],2):
            for word in page.extract_words():
                if word['x0']<35 or word['x1']>PW-33:
                    problems.append((number,'horizontal',word['text']))
                if PH-50<word['top']<PH-39:
                    problems.append((number,'footer',word['text']))
    assert not problems,problems[:15]
    # Save a report-specific register without altering the original 90-record
    # audit archive. Editorial additions are stored separately from evidence.
    filtered=[dict(record,explanatory_context=CONTEXT[record['id']]) for record in D]
    (OUT/'confirmed-defects.json').write_text(json.dumps(filtered,indent=2),encoding='utf-8')
    (OUT/'confirmed-page-map.json').write_text(json.dumps(spans,indent=2),encoding='utf-8')
    report=dict(pages=len(reader.pages),confirmed_defects=70,one_page_per_defect=True,
                detailed_pages=[spans[D[0]['id']]['start'],spans[D[-1]['id']]['end']],
                removed_records=20,removed_records_absent=True,all_original_record_fields_preserved=True,
                all_quality_context_preserved=True,contents_links=len(targets),
                last_page_reference_table=True,source_unchanged=True,
                severity_counts=dict(Counter(r['severity'] for r in D)),
                sheet_metrics=SHEET_METRICS,layout_problems=problems)
    (QA/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report


def render_all():
    doc=pdfium.PdfDocument(str(FINAL))
    for index in range(len(doc)):
        doc[index].render(scale=1.15).to_pil().save(QA/f'page-{index+1:03d}.png')
    for start in range(0,len(doc),4):
        sheet=PILImage.new('RGB',(1440,2090),'#D8DCE1')
        draw=ImageDraw.Draw(sheet)
        for offset in range(4):
            index=start+offset
            if index>=len(doc): break
            im=PILImage.open(QA/f'page-{index+1:03d}.png').convert('RGB')
            im.thumbnail((700,995))
            x=10+(offset%2)*720
            y=35+(offset//2)*1045
            sheet.paste(im,(x,y))
            draw.text((x,y-23),f'Page {index+1}',fill='#252830')
        sheet.save(QA/f'sheet-{start//4+1:02d}.jpg',quality=90)


def main():
    first=ConfirmedDoc(QA/'pagination-pass.pdf')
    first.build(make_story())
    final=ConfirmedDoc(FINAL)
    final.build(make_story(first.section_pages,first.section_ends))
    assert first.section_pages==final.section_pages
    assert first.section_ends==final.section_ends
    replace_cover()
    report=verify(final)
    render_all()
    print(json.dumps({key:value for key,value in report.items() if key!='sheet_metrics'},indent=2))
    print('Sheet spacing:',{key:round(sum(v[key] for v in SHEET_METRICS.values())/70,1)
                             for key in ('content_height_pt','unused_bottom_pt')})


if __name__=='__main__':
    main()
