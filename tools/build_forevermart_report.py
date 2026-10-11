"""Build the Part 3 report from the audited register, with charts from real counts."""
from pathlib import Path
from collections import Counter
from html import escape
import csv
import json
import math
import re
import zipfile

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               PageBreak, Image, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Circle, PolyLine
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

from build_forevermart_registry import build as build_registry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/forevermart-audit'
FINAL=ROOT/'output/pdf'
FINAL.mkdir(parents=True,exist_ok=True)
build_registry()
R=json.loads((OUT/'defect-registry.json').read_text(encoding='utf-8'))
D=[r for r in R if r['classification']=='Defect']
O=[r for r in R if r['classification']=='Observation']
SUMMARY=json.loads((OUT/'audit-summary.json').read_text())

# Portable, embedded fonts from the task host; fallback keeps the build reproducible.
fontpath=Path('C:/Windows/Fonts')
if (fontpath/'arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Report',str(fontpath/'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Report-Bold',str(fontpath/'arialbd.ttf')))
    pdfmetrics.registerFontFamily('Report',normal='Report',bold='Report-Bold',italic='Report',boldItalic='Report-Bold')
    FN,FB='Report','Report-Bold'
else:
    FN,FB='Helvetica','Helvetica-Bold'
RED=colors.HexColor('#B92F3B')
INK=colors.HexColor('#252830')
GRAY=colors.HexColor('#657080')
PALE=colors.HexColor('#F3F4F6')
BORDER=colors.HexColor('#D5D8DE')
WIDTH=516
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReport',fontName=FN,fontSize=11,leading=15,textColor=INK,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallReport',fontName=FN,fontSize=9,leading=12,textColor=GRAY,spaceAfter=5))
styles.add(ParagraphStyle(name='CellReport',fontName=FN,fontSize=9,leading=12,textColor=INK,spaceAfter=0))
styles.add(ParagraphStyle(name='CellHeadReport',fontName=FB,fontSize=9,leading=12,textColor=colors.white,spaceAfter=0))
styles.add(ParagraphStyle(name='H1Report',fontName=FB,fontSize=21,leading=25,textColor=colors.black,spaceAfter=16))
styles.add(ParagraphStyle(name='H2Report',fontName=FB,fontSize=12,leading=16,textColor=colors.black,spaceBefore=9,spaceAfter=6))
styles.add(ParagraphStyle(name='FindingTitle',fontName=FB,fontSize=17,leading=21,textColor=colors.black,spaceAfter=12))
styles.add(ParagraphStyle(name='FindingSection',fontName=FB,fontSize=11,leading=14,textColor=colors.black,spaceBefore=6,spaceAfter=4))
styles.add(ParagraphStyle(name='IndexCell',fontName=FN,fontSize=8.5,leading=10.5,textColor=INK,spaceAfter=0))
styles.add(ParagraphStyle(name='FindingBody',fontName=FN,fontSize=10.5,leading=14,textColor=INK,spaceAfter=6))
styles.add(ParagraphStyle(name='CoverTitle',fontName=FB,fontSize=32,leading=37,textColor=colors.black,spaceAfter=18))
styles.add(ParagraphStyle(name='CoverSub',fontName=FN,fontSize=15,leading=21,textColor=GRAY,spaceAfter=12))
styles.add(ParagraphStyle(name='Kicker',fontName=FB,fontSize=10,leading=14,textColor=RED,spaceAfter=9))

def clean(s):
    return str(s).replace('\u2019',"'").replace('\u2018',"'").replace('\u2013','-').replace('\u2014','-').replace('\u00a0',' ')
def p(s,style='BodyReport'):
    return Paragraph(escape(clean(s)).replace('\n','<br/>'),styles[style])
def htmlp(s,style='BodyReport'):
    return Paragraph(s,styles[style])
def label(title,text,style='FindingBody'):
    return htmlp('<b>'+escape(title)+'</b> '+escape(clean(text)),style)
def table(rows,widths=None,header=True,size='CellReport'):
    data=[[p(c,'CellHeadReport' if header and i==0 else size) for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths or [WIDTH/len(rows[0])]*len(rows[0]),hAlign='LEFT',repeatRows=1 if header else 0)
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
              ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),.35,BORDER)]
    if header:
        commands += [('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE])]
    else: commands += [('ROWBACKGROUNDS',(0,0),(-1,-1),[PALE,colors.white])]
    t.setStyle(TableStyle(commands));return t

story=[]
page_specs=[]
detail_pages={}
def page(title,items,kind='section'):
    if story: story.append(PageBreak())
    number=len(page_specs)+1
    page_specs.append(dict(page=number,title=title,kind=kind))
    story.append(p(title,'H1Report'))
    story.extend(items)
    return number
def h2(s):return p(s,'H2Report')
def caption(s):return p(s,'SmallReport')

def arrow(d,x1,y1,x2,y2,color=GRAY):
    d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=1.1))
    a=math.atan2(y2-y1,x2-x1); z=5
    d.add(Polygon([x2,y2,x2-z*math.cos(a-.5),y2-z*math.sin(a-.5),x2-z*math.cos(a+.5),y2-z*math.sin(a+.5)],fillColor=color,strokeColor=color))
def node(d,x,y,w,h,text,fill=PALE):
    d.add(Rect(x,y,w,h,fillColor=fill,strokeColor=BORDER,strokeWidth=.7))
    lines=text.split('\n')
    for i,line in enumerate(lines):
        d.add(String(x+w/2,y+h/2+((len(lines)-1)/2-i)*12-3,line,fontName=FN,fontSize=9,textAnchor='middle',fillColor=INK))

def bars(counts,title,colour=RED,height=275):
    d=Drawing(WIDTH,height);d.add(String(0,height-15,title,fontName=FB,fontSize=11,fillColor=INK))
    data=list(counts.items()); maxv=max(counts.values()) if counts else 1
    left=148; right=480; top=height-48; step=min(32,(height-75)/max(1,len(data)))
    for i,(name,v) in enumerate(data):
        y=top-i*step
        d.add(String(left-8,y+4,str(name),fontName=FN,fontSize=9,textAnchor='end',fillColor=INK))
        d.add(Rect(left,y,(right-left)*v/maxv,14,fillColor=colour,strokeColor=None))
        d.add(String(left+(right-left)*v/maxv+7,y+3,str(v),fontName=FB,fontSize=9,fillColor=INK))
    d.add(Line(left,top+20,left,top-(len(data)-1)*step-8,strokeColor=BORDER))
    return d

def pareto():
    counts=Counter(r['category'] for r in D)
    data=sorted(counts.items(),key=lambda x:-x[1]);n=len(data)
    d=Drawing(WIDTH,330);x0=35;y0=90;w=438;h=185
    maxv=max(counts.values());cum=0;points=[]
    for tick in range(0,31,5):
        y=y0+h*tick/30
        d.add(Line(x0,y,x0+w,y,strokeColor=BORDER,strokeWidth=.35))
        d.add(String(x0-8,y-3,str(tick),fontName=FN,fontSize=8,textAnchor='end'))
    for i,(name,v) in enumerate(data):
        bw=w/n*.60;x=x0+(i+.20)*w/n
        d.add(Rect(x,y0,bw,h*v/30,fillColor=RED,strokeColor=None))
        d.add(String(x+bw/2,y0+h*v/30+5,str(v),fontName=FB,fontSize=9,textAnchor='middle'))
        words=name.split();
        for j,t in enumerate(words):d.add(String(x+bw/2,y0-16-j*11,t,fontName=FN,fontSize=8,textAnchor='middle'))
        cum+=v;points += [x+bw/2,y0+h*cum/len(D)]
    d.add(PolyLine(points,strokeColor=INK,strokeWidth=1.8))
    for i in range(0,len(points),2):d.add(Circle(points[i],points[i+1],2.5,fillColor=INK,strokeColor=None))
    for q in (0,20,40,60,80,100):d.add(String(x0+w+8,y0+h*q/100-3,f'{q}%',fontName=FN,fontSize=8))
    d.add(String(0,310,'Defects by category with cumulative percentage',fontName=FB,fontSize=11))
    d.add(String(0,10,'Red bars: defect count     Charcoal line: cumulative share of the 70 defects',fontName=FN,fontSize=9,fillColor=GRAY))
    return d

def flow_purchase():
    d=Drawing(WIDTH,250)
    for x,text in [(0,'Browse\ncollection'),(134,'Choose product\nand valid size'),(268,'Review\ncart'),(402,'Checkout\nand submit')]:
        node(d,x,172,112,50,text)
        if x<402:arrow(d,x+112,197,x+134,197)
    node(d,188,68,145,52,'Server validates items,\nvariants and address')
    node(d,365,68,148,52,'Server calculates total\nand stores order')
    arrow(d,458,172,458,140);arrow(d,458,140,260,140);arrow(d,260,140,260,120)
    arrow(d,333,94,365,94)
    node(d,0,68,147,52,'Invalid request\nField-specific rejection')
    arrow(d,188,94,147,94)
    d.add(String(0,32,'Proposed correction: perform validation and pricing at the server boundary.',fontName=FN,fontSize=9,fillColor=GRAY))
    return d

def lifecycle():
    d=Drawing(WIDTH,255)
    for x,t in [(0,'New'),(132,'Triage\nauthorise'),(264,'Assigned\nfix'),(396,'Ready\nfor retest')]:
        node(d,x,170,116,47,t)
        if x<396:arrow(d,x+116,193,x+132,193)
    node(d,396,73,116,47,'QA retest')
    node(d,198,73,116,47,'Closed\nwith evidence')
    node(d,0,73,116,47,'Reopened\nreturn to fix')
    arrow(d,454,170,454,120);arrow(d,396,96,314,96)
    d.add(String(347,107,'Pass',fontName=FN,fontSize=9))
    arrow(d,396,85,116,85);d.add(String(335,67,'Fail',fontName=FN,fontSize=9))
    arrow(d,58,120,58,142);arrow(d,58,142,322,142);arrow(d,322,142,322,170)
    d.add(String(0,25,'Triage may mark Duplicate, Works as intended or New requirement with a reason.',fontName=FN,fontSize=9,fillColor=GRAY))
    return d

def fishbone():
    d=Drawing(WIDTH,290)
    d.add(Line(20,143,413,143,strokeColor=INK,strokeWidth=1.5))
    arrow(d,413,143,454,143,INK)
    node(d,431,112,82,62,'Invalid\norders\nstored',fill=colors.HexColor('#F9E9EC'))
    branches=[(90,224,'Validation','Whitespace, email,\nquantity, size'),(220,224,'Pricing','Client price and total\naccepted'),
              (345,224,'Data contracts','Names and variant\nstate mismatch'),(120,40,'UI semantics','Pointer-only actions\nand unnamed fields'),
              (290,40,'Review process','Content and negative\nchecks need gates')]
    for x,y,title,detail in branches:
        d.add(Line(x,143,x-35 if y>143 else x-30,y-16 if y>143 else y+34,strokeColor=GRAY))
        d.add(String(x-35,y,title,fontName=FB,fontSize=10,fillColor=INK))
        for k,line in enumerate(detail.split('\n')):d.add(String(x-35,y-14-k*11,line,fontName=FN,fontSize=8.5,fillColor=GRAY))
    return d

def pdca():
    d=Drawing(WIDTH,255)
    node(d,0,155,232,65,'PLAN\nApprove rules, priorities and test data')
    node(d,284,155,232,65,'DO\nCorrect server, UI and content defects')
    node(d,284,33,232,65,'CHECK\nRetest each fix and affected journeys')
    node(d,0,33,232,65,'ACT\nStandardise checks and prevent recurrence')
    arrow(d,232,187,284,187);arrow(d,400,155,400,98)
    arrow(d,284,65,232,65);arrow(d,116,98,116,155)
    return d

def footer(canvas,doc):
    canvas.saveState()
    if doc.page>1:
        canvas.setFont(FN,8);canvas.setFillColor(GRAY)
        canvas.drawString(48,758,'FOREVERMART')
        canvas.drawRightString(564,758,'SOFTWARE TESTING  |  PORTFOLIO PART 3')
    canvas.setStrokeColor(BORDER);canvas.setLineWidth(.5);canvas.line(48,39,564,39)
    canvas.setFont(FN,8);canvas.setFillColor(GRAY)
    canvas.drawString(48,26,'Quality assurance audit  |  9 October 2026  |  Version 1.0')
    canvas.drawRightString(564,26,str(doc.page))
    canvas.restoreState()

# Fixed opening pages keep navigation stable and allow a complete layout audit.
page_specs.append(dict(page=1,title='Cover',kind='cover'))
story.extend([Spacer(1,55),p('SOFTWARE TESTING  /  PORTFOLIO PART 3','Kicker'),
    p('ForeverMart','CoverTitle'),p('Software Quality Assurance Report','CoverTitle'),
    p('Detailed defect records and corrective actions','CoverSub'),Spacer(1,28),
    p('Project under test','H2Report'),htmlp('<link href="https://forevermart.vercel.app/" color="#B92F3B">https://forevermart.vercel.app/</link>'),
    Spacer(1,20),table([['Audit date','9 October 2026'],['Document version','1.0'],['Course','Software Quality Engineering and Testing'],
      ['Portfolio component','Part 3 Quality Assurance Report'],['Audit result','70 supported defects and 20 improvement observations'],
      ['Status','70 defects Open; 20 observations Review required']],[140,376],False),Spacer(1,22),
    p('Reference framework','H2Report'),p('William E. Lewis, Software Testing and Continuous Quality Improvement, second edition, with Gunasekaran Veerapillai, technical contributor. Auerbach Publications / CRC Press, 2005.'),
    caption('Prepared through a Codex-assisted audit for the project owner. This report records observations and recommended remedies; it does not claim that the remedies have been implemented.')])

page('1 Executive summary',[
    p('ForeverMart supports basic catalogue browsing, variant selection, cart use and cash-on-delivery ordering. The audit found material weaknesses in server validation and pricing, incomplete storefront actions, incorrect product content, and accessibility barriers.'),
    table([['Result','Count','Meaning'],['Supported defects','70','Reproduced behaviour or directly inspected implementation conflicts with the stated audit criterion.'],
           ['Improvement observations','20','Observed gaps needing product-owner review; excluded from the defect total.'],['Requested defect target','100','30 additional distinct defects were not established by this audit.'],
           ['Fixed or closed defects','0','No application repairs were made or retested.']],[148,53,315]),
    h2('Most urgent corrective work'),p('The order API accepted altered prices and totals, a fabricated product ID, an unsupported size, a negative fractional quantity and a malformed delivery email. The UI also accepted an empty order and unusable address data. These behaviours were confirmed using the authorised disposable account and COD test orders.'),
    h2('Readiness opinion'),p('Recommend a hold on real customer ordering until the High-severity records are corrected and independently retested. This recommendation is about the tested build and does not claim that every part of the application is broken.'),
    h2('Evidence and limits'),p('Evidence includes page captures, DOM snapshots, public product data, a publicly served client bundle, HTTP headers and responses for the audit account only. No administrator functions, real card payments, load tests, other-user records or server source code were tested.'),
    caption('Report structure adapts Lewis Appendix E29, pp. 384-385 (PDF pp. 411-412), and the E11 analysis and readiness sections, pp. 361-362 (PDF pp. 388-389).')])

toc_rows=[['Section','Pages'],['Executive summary and scope','2-5'],['Traceability and checkout decisions','6-8'],['Measurements and graphical analysis','9-13'],['Defect management and improvement plan','14-16'],['Complete finding index','17-19'],['Detailed records FM-001 to FM-090','20-109'],['Evidence plates and API results','110-115'],['Reference crosswalk and handover','116-117']]
page('2 Contents and reading guide',[
    table(toc_rows,[380,136]),Spacer(1,17),h2('How to read each finding'),
    p('Each record gives an identifier, a matching test reference, affected module and URL, discovery method, severity, priority, preconditions, reproduction procedure, expected result, actual result, impact, recommended remedy, retest acceptance and evidence paths.'),
    h2('Status and responsibility'),p('Open means the defect has been reported and has no verified repair. Review required means an observation needs a product decision. Owner roles are proposed, not assignments to named individuals. Developer and client responses have not been supplied.'),
    h2('Classification discipline'),p('Repeated symptoms in a shared implementation are grouped where appropriate. Footer links form one defect, repeated missing product names form one defect, and copied template content forms one defect. Separate server rules such as quantity, product existence, price and total are retained because they require separate validation and regression assertions.'),
    caption('Finding labels and classifications follow the intent of Lewis Chapter 24 and Appendices E12/E27, with terminology adapted to this storefront.')])

page('3 Scope and test environment',[
    table([['Area','Audit scope'],['Application','Public ForeverMart storefront and its observed application API'],['Build identity','Client asset index-r3xEth_L.js; the evidence manifest records its SHA-256. No release number or commit was provided.'],
           ['Browser','Codex in-app browser; desktop, 390 x 844 and 320 x 740 CSS-pixel viewport checks'],['Test date','9 October 2026; saved API/header evidence uses UTC timestamps'],
           ['Account','One disposable demo account; synthetic example.com contact data'],['Transactions','Eight authorised COD test orders; no real payment'],['Methods','Exploratory browser testing, boundary/negative API checks, DOM accessibility inspection and public client-code review']],[125,391]),
    h2('Included'),p('Home, Collection, search, filters, sort, product details, gallery and sizes, cart, Signup/Login, checkout, own order history, About, Contact, shared navigation, narrow-screen layout and selected response-hardening settings.'),
    h2('Excluded'),p('Admin operations, payment settlement and Stripe purchase completion, refunds, stock deduction, email delivery, rate-limit/load testing, cross-browser certification, full screen-reader certification, database access and source-level unit coverage.'),
    h2('Authorisation and cleanup'),p('The owner confirmed this is a demo site and permitted disposable accounts and test orders. Tests accessed only the audit account. The two fabricated invalid cart entries were removed. The account and eight demo orders remain as test evidence; no other-user data was changed.'),
    caption('Adapted from Lewis E4 client/server and Internet test plan, pp. 353-354 (PDF pp. 380-381), and E21 test strategy, pp. 374-375 (PDF pp. 401-402).')])

page('4 Test approach and acceptance criteria',[
    p('The course brief specifies testing, defect documentation and remedies, but supplies no detailed ForeverMart requirements. The audit therefore uses explicit ecommerce correctness rules, the behaviour advertised by the interface, and selected accessibility criteria as its baseline. Product choices and hardening recommendations are labelled observations where acceptance requires owner review.'),
    table([['Technique','Representative data or check','Purpose'],['Normal flow','Existing product, size M, quantity 1; browse, sort and cart','Establish usable baseline behaviour'],
           ['Boundary and negative values','Empty items, three spaces, -1 contact fields, quantity -0.5','Challenge required fields and integer/domain constraints'],['Identity and variant checks','Unknown product ID; QA-NOT-A-SIZE','Check references against the server catalogue'],
           ['Price integrity','$200 item with price changed to 1 or total changed to 1','Check server ownership of monetary calculations'],['State transitions','Guest to Signup; related product; browser Back','Check selection and draft persistence'],
           ['Accessibility and responsive checks','Keyboard semantics, labels, contrast, 320 CSS px reflow','Check operability and meaningful presentation']],[116,212,188]),
    h2('Severity and priority'),p('High: monetary or data-integrity risk, lost purchase state, or unnecessary authentication-data exposure. Medium: important function, content or accessibility failure. Low: limited content, structural or polish impact. P1, P2 and P3 are proposed fix order corresponding to these levels; they are not agreed delivery dates.'),
    h2('Entry and exit conditions'),p('Entry was met when the public deployment and demo test permission were available. Proposed release exit: no unresolved High defects; all remediated journeys pass positive and negative regression; remaining risks are explicitly accepted by the project owner.'),
    caption('Techniques adapt Lewis G4 Boundary Value Testing, p. 453 (PDF p. 480), G13 Equivalence Partitioning, p. 493 (PDF p. 520), and G22 Positive and Negative Testing, p. 501 (PDF p. 528).')])

page('5 Requirement and defect traceability',[
    p('These are audit criteria, not a claim that a formal requirements specification was supplied. Every detailed record maps to a test with the same numeric suffix; TC-031, for example, reproduces FM-031.'),
    table([['Criterion','Test and finding references','Expected control'],['AC-01 Store actions','FM-001, 004, 015-019','Advertised actions open or perform their declared function'],
           ['AC-02 Product truth','FM-002, 005-011, 020','Product identity, ratings, variants and names are accurate'],['AC-03 Find and retain choices','FM-012-014, 021, 036','Search normalization and state transitions preserve intent'],
           ['AC-04 Deliverable order','FM-022, 024-030, 037-038','Valid non-empty items and usable delivery data'],['AC-05 Price integrity','FM-023, 031-032','Server-derived prices, shipping and totals reconcile'],
           ['AC-06 Valid cart','FM-033-035','Existing product, valid variant, positive integer quantity'],['AC-07 Safe profile data','FM-040','Exclude authentication internals from client responses'],
           ['AC-08 Accessible operation','FM-041-066','Keyboard semantics, labels, state, contrast and reflow'],['AC-09 Accurate public copy','FM-067-070, 079','Reviewed text and consistent contacts'],
           ['AC-10 Product-owner review','FM-003, 071-078, 080-090','Decide and approve observations before treating them as defects']],[149,148,219]),
    caption('Detailed findings contain the exact expected-result assertion and proposed retest. Adapted from Lewis E6 test-case fields, p. 358 (PDF p. 385), and E29 traceability reporting, p. 384 (PDF p. 411).')])

page('6 Checkout decision table',[
    p('The table states the proposed business rules and the actual checked outcomes. A dash means the condition is irrelevant to that row; the table does not imply that every combination was executed.'),
    table([['Case','Authenticated','Valid items','Valid address','Trusted total','Expected action','Observed'],['DT-01','Yes','No, empty','Yes','-','Reject','Accepted: FM-022'],
           ['DT-02','Yes','No, qty -0.5','Yes','Yes','Reject','Accepted: FM-028'],['DT-03','Yes','No, size unknown','Yes','Yes','Reject','Accepted: FM-029'],
           ['DT-04','Yes','No, ID unknown','Yes','Yes','Reject','Accepted: FM-030'],['DT-05','Yes','Yes','No, spaces','-','Reject','Accepted: FM-024'],
           ['DT-06','Yes','Yes','No, email','Yes','Reject','Accepted: FM-027'],['DT-07','Yes','Yes','Yes','No, altered','Recalculate or reject','Accepted: FM-031/032'],
           ['DT-08','Yes','Yes','Yes','Yes','Allow COD order','Baseline demo order works']],[50,63,78,76,62,93,94]),
    h2('Boundary partitions for the next iteration'),table([['Field','Valid partition','Invalid partitions to retest'],['Quantity','Positive integer within maximum','Negative, zero, fraction, non-number, over maximum'],
           ['Product and size','Existing saleable product and supported size','Unknown ID, unavailable product, unsupported size'],['Address','Trimmed required strings and country-appropriate contact identifiers','Whitespace-only, malformed email/phone/postal code'],
           ['Money','Server catalogue and authorised adjustments','Client price, total, shipping or currency changes']],[99,195,222]),
    caption('Project-specific adaptation of Lewis G11 Decision Tables and Exhibit G.35, p. 492 (PDF p. 519).')])

page('7 Transaction workflow and control boundary',[
    p('The inspected application loads public product data, maintains cart state and submits a delivery address plus copied item data to its API. The validation and pricing results show why the trust boundary must be enforced on the server.'),
    flow_purchase(),caption('Figure 1 Proposed purchase validation workflow. This is a corrective design, not a claim that these controls already exist.'),
    table([['Boundary','Observed issue','Required remedy'],['Client to order API','Altered line price and submitted total persist','Resolve server product records and calculate final money'],
           ['Client to cart API','Unknown IDs/sizes and quantity -0.5 persist','Validate identity, variant and quantity before writing'],['Client form to order API','Spaces, -1 contact data and malformed email persist','Use one server-side address schema'],
           ['API to browser profile','password and refreshToken fields returned','Serialize an allowlisted client profile object']],[123,185,208]),
    caption('Flowchart method adapted from Lewis Chapter 3, p. 42 (PDF p. 69). The API and persistence boxes are a logical model inferred from observed requests and stored responses; server internals were not available.')])

sev=Counter(r['severity'] for r in D)
page('8 Defect severity and priority',[
    bars({s:sev[s] for s in ['High','Medium','Low']},'Supported defects by severity',height=210),
    caption('Figure 2 Counts use only the 70 supported defects. The 20 observations are excluded.'),
    table([['Severity','Count','Priority','Action'],['High',str(sev['High']),'P1','Correct before enabling real customer ordering'],['Medium',str(sev['Medium']),'P2','Repair in the next planned quality iteration'],['Low',str(sev['Low']),'P3','Correct copy and structure with focused regression']],[100,65,75,276]),
    h2('High-severity records'),p(', '.join(r['id'] for r in D if r['severity']=='High')+'.'),
    p('The severity describes observed impact; no Critical or Showstopper classification has been invented. Browser browsing continued, and monetary tests were limited to authorised demo COD orders.'),
    caption('Severity and priority are adapted from Lewis Chapter 24, pp. 265-266 (PDF pp. 292-293), and E12, p. 364 (PDF p. 391).')])

cats=Counter(r['category'] for r in D)
page('9 Pareto analysis of supported defects',[
    pareto(),caption('Figure 3 Categories are inspection classifications, not statistically proven root causes.'),
    p(f'Accessibility ({cats["Accessibility"]}) and Functionality ({cats["Functionality"]}) together account for {cats["Accessibility"]+cats["Functionality"]} of 70 defects ({(cats["Accessibility"]+cats["Functionality"])/70:.1%}). This frequency helps organise improvement work, but the fewer High-severity price and data-integrity defects still require earlier action.'),
    table([['Category','Defects','Cumulative share']]+[[name,str(v),f'{sum(x[1] for x in sorted(cats.items(),key=lambda x:-x[1])[:i+1])/70:.1%}'] for i,(name,v) in enumerate(sorted(cats.items(),key=lambda x:-x[1]))],[226,100,190]),
    caption('Adapted from Lewis G21 Pareto Analysis and Exhibit G.43, pp. 499-501 (PDF pp. 526-528). The 80/20 relationship is not assumed to hold for this dataset.')])

mods=Counter(r['module'] for r in D)
page('10 Defect distribution by application area',[
    bars(dict(sorted(mods.items(),key=lambda x:-x[1])),'Supported defects by module',height=420),
    caption('Figure 4 Each record is counted once in its primary module; shared symptoms are described in that record.'),
    p('These counts identify where the audit encountered problems. They do not measure the relative quality of equally tested modules, because the amount of testing in each area was not equal.'),
    p('A server validator change should trigger order and cart API retests. A shared navigation or title change should trigger all-route keyboard and responsive regression.'),
    caption('Adapted from the category and system-area analyses in Lewis Chapter 24, pp. 263-267 (PDF pp. 290-294), and E29, p. 385 (PDF p. 412).')])

page('11 Status and measurement boundaries',[
    bars({'Open defects':70,'Review observations':20,'Verified closed':0},'Current record status',height=215),
    caption('Figure 5 Status counts describe this audit handover, not a development-team dashboard.'),
    table([['Metric','Reported value or limitation'],['Requested defect count','100'],['Established distinct defects','70; target shortfall 30'],['Additional observations','20; not included in the defect count'],
           ['Closure count','0; no repair or closure evidence received'],['Defect density per KSLOC','Not calculated: server source and valid source-size denominator unavailable'],['Test coverage percentage','Not calculated: no complete requirements or test denominator supplied'],
           ['Defect age and closure trend','Not calculated: no repair history or closure dates'],['Performance and load curves','Not measured; no fabricated response-time, throughput or control-chart data']],[205,311]),
    caption('Lewis describes defect age and density on p. 267 (PDF p. 294) and tracking curves in Exhibit 24.1, p. 264 (PDF p. 291). Those charts require a time series or size data not present here; they have not been copied with invented values.')])

page('12 Cause and effect investigation',[
    fishbone(),caption('Figure 6 Investigation map adapted to ForeverMart. Branches are possible contributing factors; the server root cause has not been confirmed from source.'),
    table([['Evidence-backed factor','Investigation or prevention action'],['Order validation failures','Inspect request schemas and write-path checks for empty items, identity, variant, quantity and address'],
           ['Monetary values persist as submitted','Locate server price calculation and determine why client money is accepted'],['Client data-contract mismatch','Standardise productName and variant state transitions across views'],
           ['UI semantics and copied content','Review shared components with keyboard, labels and content checks before release']],[220,296]),
    p('Confirm causes through server-code review and a reproduction after each fix. A common symptom or a large category count alone does not prove a single causal mechanism.'),
    caption('Adapted from Lewis cause-and-effect discussion, p. 42 (PDF p. 69), and G7 Cause-Effect Graphing, pp. 456-457 (PDF pp. 483-484).')])

page('13 Defect lifecycle and triage',[
    lifecycle(),caption('Figure 7 Proposed defect handling workflow, adapted from Exhibit 24.2. It has not been executed by the development team.'),
    table([['Role','Proposed responsibility'],['Project owner','Confirm requirements, review observations and accept any residual risk'],['QA reviewer','Check evidence, reproduce, consolidate duplicates and specify retest acceptance'],
           ['Developer','Investigate cause, implement the remedy and identify the fix build'],['QA retester','Retest the original scenario and related regression before closing']],[135,381]),
    h2('Closure evidence'),p('A record closes only after the actual corrected build is identified, the original failure no longer occurs, relevant positive and negative checks pass, and fresh evidence is attached. If it fails, reopen it with the new actual result. No record in this report is marked fixed.'),
    caption('Adapted from Lewis Exhibit 24.2, p. 266 (PDF p. 293), defect meetings, p. 265 (PDF p. 292), and E12 status fields, p. 364 (PDF p. 391).')])

page('14 Continuous improvement plan',[
    pdca(),caption('Figure 8 Project-specific Plan Do Check Act cycle. Proposed actions are not completed work.'),
    table([['Phase','Deliverable','Acceptance evidence'],['Plan','Approve domain rules, severity and supported countries/currency','Reviewed criteria and an owner decision for each observation'],
           ['Do','Repair server validation/pricing, cart merge, controls and product copy','Identified fix build and developer change notes'],['Check','Run record-specific retests and critical shopping regression','Expected/actual results plus fresh screenshots or responses'],
           ['Act','Add shared schemas, typed contracts, accessibility and content gates','Repeatable checks in the release workflow']],[55,223,238]),
    p('Suggested work order: first protect server order/cart integrity and profile serialization; then restore missing actions and customer state; then correct shared accessibility and content; finally review the optional hardening and optimisation observations.'),
    caption('Adapted from Lewis Exhibit 3.1 and PDCA explanation, pp. 48-50 (PDF pp. 75-77), and E20 PDCA Test Schedule, p. 373 (PDF p. 400).')])

page('15 Corrective action and regression matrix',[
    table([['Changed component','Record references','Retest scope'],['Order validation and price calculation','FM-022-032','Valid COD order; invalid items and address; tampered money; confirmation totals'],
           ['Cart validators and authentication merge','FM-020-021, 033-035','Guest and account carts; valid variants; bounds; unknown references; item display'],['Product and recommendation state','FM-004-011, 045, 055, 062','Accurate data; related navigation; gallery; variants; keyboard and alternatives'],
           ['Collection/search state','FM-012-014, 041-042, 052, 056','Search normalization; empty state; filters/sort; Back; keyboard'],['Shared navigation and forms','FM-015-019, 043-044, 048-066','All routes; input names; focus; menu lifecycle; 320 px layout'],
           ['Public content and configuration','FM-067-090 as applicable','Proofread pages; verify approved contacts/policies; check headers and metadata']],[154,123,239]),
    h2('Passing checks retained as regression baselines'),p('The audit observed successful catalogue loading and normal image loading, correctly labelled category checkboxes, case-insensitive basic search, working price sorting, a size-required add-to-cart check, a quantity minimum of one in normal decrement controls, working signup/login/logout, 390 px reflow, a working favicon, HTTPS/HSTS and a 401 response when the own-cart request omitted authentication.'),
    h2('Approval remains pending'),p('The project owner has not approved the inferred criteria, assigned remedies or accepted production risk. Developer and client comments remain Not supplied. Suggested delivery order is not a promised implementation schedule.'),
    caption('Adapted from Lewis E14 Retest Matrix, pp. 366-367 (PDF pp. 393-394). The matrix maps changes to tests; it does not claim those retests have been run.')])

# Index pages with concise, readable rows.
for start in (0,30,60):
    rows=[['ID','Finding','Type','Severity']]
    rows += [[r['id'],r['title'],'Defect' if r['classification']=='Defect' else 'Review',r['severity']] for r in R[start:start+30]]
    index=table(rows,[52,333,59,72],size='IndexCell')
    index.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    page(f'16 Finding index {start+1} to {start+30}',[index])

# Full E12-style sheet for every finding, with the remedy and acceptance criterion.
for r in R:
    if story:story.append(PageBreak())
    n=len(page_specs)+1
    detail_pages[r['id']]=n
    page_specs.append(dict(page=n,title=f"{r['id']} {r['title']}",kind='finding'))
    meta=table([['Module',r['module'],'Severity / priority',r['severity']+' / '+r['priority']],
               ['Test reference',r['test_id'],'Status',r['status']],['Detected','9 October 2026','Proposed owner',r['proposed_owner']]],[79,179,105,153],False),Spacer(1,7),
    # Keep record metadata compact while the body remains comfortably readable.
    meta=meta[0]
    meta.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    fh=lambda text:p(text,'FindingSection')
    story.extend([p(r['id']+'  /  '+r['classification'].upper(),'Kicker'),p(r['title'],'FindingTitle'),meta,Spacer(1,7),
        label('Location',r['url']),label('Method',r['method']),label('Preconditions',r['preconditions']),fh('Reproduction procedure')])
    for i,step in enumerate(r['steps'],1):story.append(p(f'{i}. {step}','FindingBody'))
    story.append(table([['Expected result','Actual result'],[r['expected'],r['actual']]],[258,258]))
    story.extend([Spacer(1,7),label('Impact',r['impact']),fh('Recommended remedy'),p(r['remedy'],'FindingBody'),
                  fh('Retest acceptance'),p(r['retest'],'FindingBody'),fh('Evidence'),
                  p('; '.join(r['evidence']),'SmallReport')])
    if r['note']:story.append(label('Audit note',r['note'],'SmallReport'))
    story.append(caption('Unassigned; no fix build or closure. Developer and client comments: not supplied. Adapted from Lewis E12/E27.'))

assets=OUT/'report-assets';assets.mkdir(exist_ok=True)
def screenshot(name,crop_height=720,maxwidth=516):
    im=PILImage.open(OUT/'evidence'/name).convert('RGB')
    w,h=im.size
    im=im.crop((0,0,w,min(h,crop_height)))
    dest=assets/(Path(name).stem+'-excerpt.jpg');im.save(dest,quality=88)
    pw=min(maxwidth,w);ph=pw*im.height/im.width
    return Image(str(dest),width=pw,height=ph,hAlign='LEFT')

page('17 Visual evidence of storefront failures',[
    h2('FM-001 and FM-067 Hero action and spelling'),screenshot('shop-now-no-action.jpg',540),
    caption('Figure 9 Unaltered top excerpt of the saved storefront capture. SHOP NOW did not navigate. The full original is in the evidence folder.'),
    h2('FM-008 Product image and identity'),screenshot('product-details.jpg',610),
    caption('Figure 10 Product page excerpt showing the garment image, product name and price. Originals and DOM data are retained.')])
page('18 Visual evidence of incomplete customer actions',[
    h2('FM-020 Cart row without its product name'),screenshot('cart-one-item.jpg',535),
    caption('Figure 11 The row retains image and amounts, but not its productName.'),
    h2('FM-022 and FM-023 Empty-cart checkout'),screenshot('cart-empty.jpg',535),
    caption('Figure 12 Empty cart, conflicting shipping/total and an enabled checkout action. The server-side empty order is also retained in demo-orders.json.')])
page('19 Visual evidence of invalid input and descriptions',[
    h2('FM-024 to FM-026 Invalid delivery values'),screenshot('checkout-invalid-values.jpg',565),
    caption('Figure 13 Delivery-form excerpt from the invalid COD test. Persisted values are shown in the API evidence table.'),
    h2('FM-006 Incorrect jacket description'),screenshot('second-product-loaded.jpg',590),
    caption('Figure 14 The jacket description discusses a round-neck short-sleeved shirt. The evidence file retains the full page.')])
page('20 Visual evidence of missing-record handling',[
    h2('FM-011 Unknown product'),screenshot('missing-product.jpg',555),
    caption('Figure 15 Missing product leaves incomplete purchase controls.'),
    h2('FM-039 Unknown route'),screenshot('unknown-route.jpg',495),
    caption('Figure 16 Unknown route has no explanation or recovery body. The shared header and footer remain.')])

im1=screenshot('checkout-320-verified.jpg',740,175)
im2=screenshot('mobile-menu-open.jpg',844,175)
paired=Table([[im1,im2]],colWidths=[258,258],hAlign='LEFT')
paired.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
page('21 Mobile and accessibility evidence',[
    p('The left capture reproduces checkout at 320 CSS pixels. The right shows the menu state at the inspected mobile size.'),paired,
    caption('Figure 17 Left: document width 352 px at viewport 320 px, FM-066. Right: the mobile navigation whose interaction semantics and dismissal were inspected, FM-048 to FM-051.'),
    table([['Measurement','Observed value'],['Muted text colour','Approximately RGB 153, 161, 175 on white'],['Text size','16 CSS px'],['Contrast ratio','2.60:1; normal-text criterion 4.5:1']],[235,281]),
    caption('Contrast comes from the recorded computed OKLCH colour and the saved conversion, not from sampling a compressed screenshot.')])

page('22 API and persistence evidence',[
    table([['Test','Submitted boundary value','Response and read-back'],['Order total','Valid $200 item, quantity 1; amount=1','HTTP 200 success; amount 1 stored'],
           ['Order line price','price=1, amount=11 for the $200 product','HTTP 200 success; altered price stored'],['Order quantity','quantity=-0.5','HTTP 200 success; quantity stored and displayed'],
           ['Order variant','size=QA-NOT-A-SIZE','HTTP 200 success; unsupported size stored'],['Order identity','ID=000000000000000000000000','HTTP 200 success; fabricated reference stored'],
           ['Order delivery email','address.email=not-an-email','HTTP 200 success; malformed value stored'],['UI delivery address','Whitespace-only required strings; phone=-1; zip=-1','Order stored with those values'],
           ['UI empty order','items=[]','Order stored with amount 10'],['Cart boundary checks','Unknown ID, unsupported size and quantity=-0.5','Each accepted; invalid demo entries later removed'],
           ['Authentication baseline','Own cart request with no authentication cookie','HTTP 401; no anonymous access demonstrated']],[103,200,213]),
    h2('Sensitive response fields'),p('The own-profile response field names included password and refreshToken. Values were excluded from the evidence register and this document. Returning these fields is an exposure finding; this audit does not claim plaintext passwords or access to other users.'),
    h2('Evidence sources'),p('raw/api-validation.json contains the six API order checks and own-order read-back. raw/demo-orders.json contains the earlier two UI orders. raw/cart-validation.json contains cart checks. All submitted identity and contact data are synthetic.'),
    caption('The server root cause is not asserted without source access. Remedies specify enforceable rules derived from the observed failures.')])

page('23 Reference book crosswalk',[
    p('The attached reference is Software Testing and Continuous Quality Improvement, second edition, William E. Lewis, with Gunasekaran Veerapillai as technical contributor. Copyright 2005, Auerbach Publications / CRC Press, ISBN 0-8493-2524-2. Printed page n corresponds to PDF page n+27 for the cited numbered pages.'),
    table([['Book reference','Printed / PDF pages','Application in this report'],['E4 Internet/client-server test plan','353-354 / 380-381','Scope, assumptions, environment and exclusions'],['E6 test-case fields','358 / 385','Matching TC reference and expected/actual results'],
           ['E11 system summary','361-362 / 388-389','Capabilities, deficiencies, risk and readiness opinion'],['E12 problem report','362-364 / 389-391','Detailed finding sheets and lifecycle metadata'],['E14 retest matrix','366-367 / 393-394','Change-to-regression mapping'],
           ['E20 PDCA schedule; E21 strategy','373-375 / 400-402','Improvement stages and test approach'],['E27 defect table; E29 summary','383-385 / 410-412','Index, register, summary and classifications'],['Exhibit 24.2 defect lifecycle','266 / 293','Proposed triage, fix, retest, reopen and closure flow'],
           ['Exhibit 3.1 PDCA circle','49 / 76','ForeverMart improvement cycle'],['G7 cause and effect','456-457 / 483-484','Hypothesis-based investigation diagram'],['G11 decision tables','492 / 519','Checkout decision table'],['G21; Exhibit G.43 Pareto','499-501 / 526-528','Actual category counts and cumulative percentage']],[166,125,225]),
    p('Figures and tables are original adaptations populated with ForeverMart evidence. Unrelated book examples have not been copied. Run, scatter, control and defect-age charts require measurements not gathered in this audit, so no fabricated series is included.'),
    caption('The book was extracted in full for navigation, and the relevant reporting, management and testing-technique sections and representative layouts were reviewed.')])

refs=[('W3C WCAG 2.2 Labels or Instructions','https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html'),
      ('W3C WCAG 2.2 Keyboard','https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html'),
      ('W3C WCAG 2.2 Name Role Value','https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html'),
      ('W3C WCAG 2.2 Contrast Minimum','https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html'),
      ('W3C WCAG 2.2 Reflow','https://www.w3.org/WAI/WCAG22/Understanding/reflow.html'),
      ('OWASP REST Security Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html'),
      ('MDN Content Security Policy','https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy')]
ref_paragraphs=[htmlp(f'<link href="{url}" color="#B92F3B">{escape(title)}</link>','SmallReport') for title,url in refs]
page('24 Handover and supporting references',[
    p('The course assignment requires testing a project, documenting defects and providing remedies. This report addresses Part 3 for ForeverMart. It does not replace the handwritten Part 1/2 work or claim the separate Python numerical simulation has been retested here.'),
    h2('Included deliverables'),table([['File or folder','Use'],['ForeverMart_Quality_Assurance_Report.pdf','Readable report with individual records, tables, figures and evidence excerpts'],['defect-registry.csv and .json','Editable complete register, suitable for filtering or importing into a defect tracker'],
           ['ForeverMart_Quality_Assurance_Report.md','Editable text companion with the same detailed records'],['evidence and raw folders','Original captures and sanitized test evidence; filenames map from each finding'],['manifest.json','File hashes, classifications and report counts for handover integrity']],[209,307]),
    h2('Supporting standards and guidance'),*ref_paragraphs,
    h2('Next review'),p('The owner should confirm the audit criteria, accept or reject the 20 observations, assign remedies, and provide a fix build for retesting. Further testing may establish additional defects; the requested total of 100 remains unfulfilled by 30 confirmed records.'),
    caption('Accessibility findings are targeted checks, not a complete WCAG conformance certification. HTTP-header observations are defence-in-depth recommendations, not demonstrated attacks.')])

pdf=FINAL/'ForeverMart_Quality_Assurance_Report.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=letter,rightMargin=48,leftMargin=48,topMargin=55,bottomMargin=51,
    title='ForeverMart Software Quality Assurance Report',author='Codex-assisted QA audit',subject='Software Testing Portfolio Part 3',pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'report-page-plan.json').write_text(json.dumps(page_specs,indent=2),encoding='utf-8')

# Editable text companion; the PDF is the primary visual report.
md=['# ForeverMart Software Quality Assurance Report','',
    'Software Testing Portfolio Part 3 | 9 October 2026 | Version 1.0','',
    '70 supported defects and 20 separately labelled improvement observations. The requested target of 100 defects was not established. No fixes are claimed.','',
    'Reference: William E. Lewis, Software Testing and Continuous Quality Improvement, second edition, Auerbach / CRC Press, 2005. Detailed records adapt E12 and E27.','',
    '## Scope','', 'Public storefront, browser/DOM checks, public client-code review and own disposable-account API tests. Eight authorised COD orders; no real payment. Admin functions, other-user data, load tests and card settlement were excluded.','']
for r in R:
    md += [f"## {r['id']} {r['title']}",'',f"**{r['classification']} | {r['severity']} | {r['priority']} | {r['status']}**",'',
           f"Module: {r['module']}  ",f"Test: {r['test_id']}  ",f"Location: {r['url']}  ",f"Method: {r['method']}  ",
           f"Proposed owner: {r['proposed_owner']} (not assigned)",'',f"Preconditions: {r['preconditions']}",'',
           '### Reproduction','']+[f'{i}. {s}' for i,s in enumerate(r['steps'],1)]+['',
           f"**Expected:** {r['expected']}",'',f"**Actual:** {r['actual']}",'',f"**Impact:** {r['impact']}",'',
           f"**Recommended remedy:** {r['remedy']}",'',f"**Retest acceptance:** {r['retest']}",'',
           '**Evidence:** '+', '.join(r['evidence']),'',f"Audit note: {r['note'] or 'None'}",'',
           'Developer/client comments: not supplied. Close date: not closed.','']
md += ['## Supporting references','']+[f'- [{a}]({b})' for a,b in refs]
(OUT/'ForeverMart_Quality_Assurance_Report.md').write_text('\n'.join(md),encoding='utf-8')
manifest=dict(report=str(pdf.name),audit_date='2026-10-09',defects=70,observations=20,
    target_defects=100,shortfall=30,report_pages_planned=len(page_specs),files={})
for folder in ['evidence','raw']:
    for f in sorted((OUT/folder).glob('*')):
        if f.is_file():manifest['files'][f'{folder}/{f.name}']=dict(bytes=f.stat().st_size,sha256=__import__('hashlib').sha256(f.read_bytes()).hexdigest())
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Created PDF:',pdf)
print('Planned pages:',len(page_specs))
