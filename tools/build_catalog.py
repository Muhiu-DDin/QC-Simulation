"""Transcribed numerical inputs. Run only when intentionally rebuilding the catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cases = []
def add(id, kind, page, title, inputs, note=''):
    cases.append(dict(id=id, kind=kind, page=page, pdf_page=page+15,
                      title=title, inputs=inputs, interpretation=note))

sc = [(9,26.7,5.3),(17,138.6,15.1),(4,84.2,9.6),(22,8.1,7.4)]
for i,(n,m,r) in enumerate(sc):
    for ex,kind,page in [('SC10-1','xbar',477),('SC10-3','range',484)]:
        add(f'{ex}{chr(97+i)}',kind,page,'Control limits',dict(n=n,mean=m,rbar=r))
tire = dict(n=5,means=[50.5,49.7,50,50.7,50.7,50.6,49.8,51.1,50.2,50.4,50.6,50.7],
            ranges=[1.1,1.6,1.8,.1,.9,2.1,.3,.8,2.3,1.3,2,2.1],unit='thousand miles')
add('SC10-2','xbar',478,'Altoona tires',tire,'No points exceed mean-chart limits. The range chart must also be examined.')
add('SC10-4','range',485,'Altoona tire variability',tire,'The book identifies cycling in ranges; absence of outliers alone does not establish control.')
for i,(n,p) in enumerate([(144,.1),(60,.9),(125,.36),(48,.75)]):
    add(f'SC10-5{chr(97+i)}','p',491,'Proportion limits',dict(n=n,p=p))
meals=[89.33,81.33,95.33,88.67,96,86.67,98,84,90.67,80.67,88,86.67,96.67,85.33,78.67,89.33,89.33,78.67,94,94,99.33,95.33,94.67,92.67,81.33,89.33,99.33,90.67,92,88]
add('SC10-6','p',491,'Meals on Wheels',dict(n=150,proportions=[x/100 for x in meals],attribute='on time'),
    'Days 2, 10, 15, 18 and 25 are below LCL. High on-time days also exceed UCL statistically, although they are favorable. Investigate routes, traffic and driver training. Percentages are used as printed, without reconstructing counts.')
add('SC10-7','pareto',498,'Northway component faults',dict(counts={'CPU':25,'Floppy disk drives':106,'Hard disk drive':237,'I/O ports':36,'Keyboard':60,'Monitor':42,'Power supply':186,'RAM memory':30,'ROM BIOS':7,'Video adapter':47,'Other':163}),
    'Prioritize hard-disk and power-supply vendors. Other remains last, as in the chapter convention.')
for ex,page,ps,plans,N,risk in [('SC10-8',505,[.005]*4,[(150,1),(150,2),(200,1),(200,2)],2000,'producer'),('SC10-9',505,[.01]*4,[(150,1),(150,2),(200,1),(200,2)],2000,'consumer')]:
    for i,((n,c),p) in enumerate(zip(plans,ps)):
        add(f'{ex}{chr(97+i)}','acceptance',page,'Single sampling risk',dict(n=n,c=c,N=N,p=p,risk=risk,model='binomial'))

add('10-12a','xbar',478,'Known standard error',dict(n=12,mean=16.4,se=1.2),
    'The given 1.2 is sigma of the sample mean, not individual sigma. Do not divide it by sqrt(n) again.')
for suffix,n,m,r in [('b',12,16.4,7.6),('c',8,4.1,1.3),('d',15,141.7,18.6)]:
    add('10-12'+suffix,'xbar',478,'Mean control limits',dict(n=n,mean=m,rbar=r))
piston=dict(n=8,means=[15.85,15.95,15.86,15.84,15.91,15.81,15.86,15.84,15.83,15.83,15.72,15.96,15.88,15.84,15.89],ranges=[.15,.17,.18,.16,.14,.21,.13,.22,.19,.21,.28,.12,.19,.22,.24],unit='cm')
add('10-13','xbar',478,'Wilson pistons',piston,'Batch 11 is below LCL; batches 2 and 12 exceed UCL. Investigate tooling, setup and measurement; correct identified causes before changing the baseline.')
add('10-19','range',485,'Wilson piston variability',piston,'Review ranges together with the mean-chart signal at batch 11.')
ems=dict(n=9,means=[11.6,17.4,14.8,13.8,13.9,22.7,16.6,9.5,12.7,17.7,16.3,10.5,22.5,12.6,11.4,16,11,13.3,9.3,21.5,17.9],ranges=[14.1,19.1,22.9,18,14.6,23.7,21,12.6,17,12,15.1,22.1,24.1,21.3,12.1,21.1,13.5,20.3,16.8,20.7,23.2],unit='minutes')
for id,kind,page in [('10-14','xbar',478),('10-20','range',485)]:
    add(id,kind,page,'Emergency response times',ems,'Saturdays are groups 6, 13 and 20. Demand is higher; review staffing and dispatch. Saturday ranges are high within each week. Recalculation below is justified by the assigned cause in the exercise.')
    reduced={**ems,'means':[v for i,v in enumerate(ems['means']) if i%7!=5], 'ranges':[v for i,v in enumerate(ems['ranges']) if i%7!=5], 'labels':[str(i+1) for i in range(21) if i%7!=5]}
    add(id+'c',kind,page,'Emergency service, Saturdays excluded',reduced,'Only known Saturday observations are excluded. All remaining means are within limits; continue checking for patterns.')
bearings=[
[5.03,5.06,4.86,4.90,4.95],[4.97,4.94,5.09,4.78,4.88],[5.02,4.98,4.94,4.95,4.80],
[4.92,4.93,4.90,4.92,4.96],[5.01,4.99,4.93,5.06,5.01],[5,4.95,5.10,4.85,4.91],
[4.94,4.91,5.05,5.07,4.88],[5,4.98,5.05,4.96,4.97],[4.99,5.01,4.93,5.10,4.98],
[5.03,4.96,4.92,5.01,4.93],[5.02,4.88,5,4.98,5.09],[5.09,5.01,5.13,4.89,5.02],
[4.90,4.93,4.97,4.98,5.12],[5.04,4.96,5.15,5.04,5.02],[5.09,4.90,5.04,5.19,5.03],
[5.10,5.01,5.04,5.05,5.02],[4.97,5.10,5.12,4.92,5.04],[5.01,4.99,5.06,5.04,5.12]]
for id,kind,page in [('10-15','xbar',479),('10-21','range',486)]:
    add(id,kind,page,'Track ball bearings',dict(n=5,observations=bearings,unit='mm'),
        'Means show a rise over time, including a long sequence above the center line late in the series. Investigate tool drift; ranges alone may not signal it.')
bracket=dict(n=15,means=[4,4.02,4.01,4,4.03,4.01,4.03,4,4.03,4.06,4.04,4.06,4.04,4.03,4.06,4.05,4.01,4.01,4,4.02,3.99,4.02,4,4],ranges=[.09,.10,.10,.11,.09,.11,.11,.10,.12,.11,.09,.10,.11,.09,.10,.10,.10,.11,.10,.09,.10,.11,.09,.09],unit='inches')
for id,kind,page in [('10-16','xbar',480),('10-22','range',486)]:
    add(id,kind,page,'Northern White Metals brackets',bracket,'The second shift (groups 9-16) has higher means. Check saw recalibration between shifts; examine both charts.')
for i,(n,m,r) in enumerate([(3,18.4,3.1),(19,16.2,6.9),(8,141.7,18.2),(24,8.6,1.4)]):
    add('10-17'+chr(97+i),'range',485,'Range limits',dict(n=n,mean=m,rbar=r))
add('10-17e','range_identity',485,'Recover upper range limit',dict(rbar=6,lcl=3),'For positive LCL, symmetric limits imply UCL = 2 Rbar - LCL = 9. No sample size is supplied.')
for i,(n,p) in enumerate([(30,.25),(65,.15),(82,.05),(97,.42),(124,.63)]):
    add('10-24'+chr(97+i),'p',492,'Proportion limits',dict(n=n,p=p))
add('10-25','p',492,'Airline luggage delivery',dict(n=200,proportions=[.89,.91,.93,.95,.94,.96,.92,.91,.93,.90,.88,.94,.97,.94,.95,.92,.93,.92,.91,.93,.89],attribute='correct delivery'),
    'No individual limit violations. Stable performance is not necessarily satisfactory: investigate incorrect deliveries and improve the system.')
bad=[2.4,1.8,1.6,.6,1,1.4,2,2.8,2.4,1.6,1,.4,.6,1.6,2.2,2.6,2.2,1.6,1,.4,1.2,1.6,2.2,2.8,1.8,1.6,.8,.4,1.2,1.4,2,2.8]
add('10-26b','p',492,'BioAssist capsules',dict(n=500,p=.015,proportions=[x/100 for x in bad]),'Repeated cycles remain even when points are inside limits. Investigate periodic equipment or calibration effects.')
add('10-26a','proportion_test',492,'BioAssist aggregate test',dict(n=16000,successes=round(sum(bad)/100*500),p0=.015,alpha=.05),'H0: p = .015; H1: p > .015. Alpha .05 is a project assumption; failing to reject does not prove compliance.')
add('10-27','p',493,'Stock-market chart design',dict(n=100,p=.5),'CL .5, limits .35 and .65. No observations are provided. Stocks and days may be dependent, violating the simple binomial model; the chart alone cannot prove the belief.')
add('10-28','p',493,'Late flight departures',dict(n=240,counts=[26,19,26,22,24,19,19,20,18,18,17,9,13,10,12,14,14,13,9,10,12,15,14,15,16,18,17,16,18,17]),'Procedures began after day 10. Compare first, middle and final ten days; initial improvement is followed by deterioration. A single pooled chart can mask intervention effects.')
rows=[('Omitted advertisement','Classified',18),('Incorrect special instructions','Classified',37),('Typographical error in news','Reporting',14),('Advertisement in wrong section','Classified',16),('Incorrectly priced advertisement','Classified',8),('Factual error in news','Reporting',16),('Late delivery of all papers','Printing',3),('Advertisement on incorrect date','Classified',6),('Typographical error in commercial advertisement','Advertising',8),('Failure to respond to news report','Reporting',16),('Editorialized factual story','Reporting',2),('Misquoted news story','Reporting',4),('Incorrect size of advertisement','Classified',7),('Incorrect phone number in advertisement','Classified',9),('Incorrect address in advertisement','Classified',3)]
departments={}
for _,d,c in rows: departments[d]=departments.get(d,0)+c
add('10-31a','pareto',498,'Newspaper departments',dict(counts=departments),'Classified is the first department to investigate.')
add('10-31b','pareto',498,'Classified advertisement errors',dict(counts={label:c for label,d,c in rows if d=='Classified'}),'Incorrect special instructions are the largest category. Review order capture and proofing with staff.')
add('10-32','pareto',499,'Zippy Cola plants',dict(counts={'Atlanta':267,'Boston':23,'Chicago':37,'Houston':175,'Milwaukee':19,'New Orleans':78,'San Francisco':28,'Seattle':43}),'Visit Atlanta and Houston first. Counts do not account for different production volumes.')
for ex,page,p,plans,N,risk in [('10-36',505,.02,[(175,3),(175,5),(250,3),(250,5)],1500,'producer'),('10-37',506,.03,[(175,3),(175,5),(250,3),(250,5)],1500,'consumer'),('10-47',512,.01,[(200,1),(200,2),(250,1),(250,2)],2500,'producer'),('10-48',512,.015,[(200,1),(200,2),(250,1),(250,2)],2500,'consumer')]:
    for i,(n,c) in enumerate(plans): add(ex+chr(97+i),'acceptance',page,'Single sampling risk',dict(n=n,c=c,N=N,p=p,risk=risk,model='binomial'))
for ex,page,n,c,N,risk,ps in [('10-38',506,250,2,2500,'producer',[.005,.01,.015]),('10-39',506,250,2,2500,'consumer',[.01,.015,.02]),('10-55',514,300,3,3000,'producer',[.005,.01,.015]),('10-56',514,300,3,3000,'consumer',[.01,.015,.02])]:
    for i,p in enumerate(ps): add(ex+chr(97+i),'acceptance',page,'Read risk from OC graph',dict(n=n,c=c,N=N,p=p,risk=risk,model='poisson'),
        'The plotted points agree with a Poisson OC approximation (lambda=n*p). Use that model for the graph-reading comparison; also report the binomial probability. Graph readings have limited precision.')
audits=[2,1,2,3,5,4,5,6,3,1,1,3,2,2,3,2]
add('10-40a','proportion_test',511,'Audit aggregate test',dict(n=2000,successes=sum(audits),p0=.02,alpha=.05),'H0: p=.02; H1: p>.02. Alpha .05 is assumed; failing to reject is not proof that the target is met.')
add('10-40b','p',511,'Weekly audit chart',dict(n=125,p=.02,counts=audits),'The rise toward the filing deadline warrants investigation even though individual points are inside limits.')
checks=dict(n=10,means=[49.4,49.9,48.8,50.1,49.7,48.1,48.6,48.7,50.7,51.3,51.1,51.6,50,50.5,51.4,50.1],ranges=[4,7,7,4,7,10,7,10,6,4,9,9,6,7,4,7],unit='checks per two minutes')
for id,kind in [('10-44','xbar'),('10-45','range')]: add(id,kind,512,'Global Bank check encoding',checks,'All first-shift means are below CL and all second-shift means above CL. Investigate operator, equipment and shift conditions; ranges do not show the same shift.')
add('10-46','pareto',512,'Construction punch-list problems',dict(counts={'Electrical':257,'Flooring':23,'Heating/AC':35,'Painting':19,'Plumbing':22,'Roofing':31,'Tile':51,'Wallboard':303,'Windows':16,'Other':68}),'Wallboard and electrical account for most problems. Multiple problems may occur in one condo; total faults is not the number of defective condos.')
disk=dict(n=24,means=[75.3,75,74.8,75,75.3,74.8,74.8,74.9,74.6,74.9,75.2,75.1,74.8,74.9,74.9,75.1,75,74.9,74.9,75.1],ranges=[3.2,3.3,3.6,3.5,3.8,3.7,3.4,3.3,3.4,3.1,3.1,3,3.1,2.9,2.8,2.8,2.7,2.9,2.8,2.9],unit='microns')
add('10-50','xbar',513,'Reliant disk coating means',disk,'The last ten means vary less than the first ten. Mean-chart control limits are distinct from the individual specification 72-78 microns.')
add('10-51','range',513,'Reliant coating variability',disk,'Ranges decline and the last ten are all below CL. Reduced variation may be an improvement; identify the cause, sustain it, then establish a new baseline. The change explains tighter sample means.')
add('10-52','p',513,'Photomatic print quality',dict(n=2000,p=.001,counts=[3,1,2,4,4,2,2,3,1,0,2,2,1,3,2,2,0,4,2,0]),'No points exceed limits. A p chart evaluates stability relative to the target; it does not prove the manufacturer specification is satisfied.')

ROOT.joinpath('data').mkdir(exist_ok=True)
ROOT.joinpath('data/chapter10_inputs.json').write_text(json.dumps(dict(schema_version=1,cases=cases),indent=2),encoding='utf-8')
print(f'Wrote {len(cases)} numerical cases')
