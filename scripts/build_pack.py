"""Build reproducible synthetic quality-reporting source tables and evidence."""
from __future__ import annotations
import csv, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
random.seed(27)
facilities = [("North Valley","North",420),("Canyon View","North",310),("Wasatch","Central",510),("Lakeview","Central",380),("Red Rock","South",295),("Mesa Ridge","South",340)]
months = [f"2025-{m:02d}" for m in range(1,13)]

def write(name, fields, rows):
    path = ROOT / ('data' if '/' not in name else '') / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

encounters=[]; discharges=[]; safety=[]; experience=[]; refresh=[]
eid=1
for facility, region, base in facilities:
  for month_i, month in enumerate(months, 1):
    for _ in range(base//4):
      los=round(max(.5, random.gauss(3.6+(month_i%3)*.1,1.3)),1)
      complete=random.random()>.028
      encounters.append(dict(encounter_id=f"E{eid:05}",facility=facility,region=region,month=month,service_line=random.choice(['Medical','Surgical','Cardiac','Orthopedic']),length_of_stay_days=los,record_complete='Y' if complete else 'N'))
      if random.random()<.91:
        readmit=random.random() < (.132 if facility in ['Canyon View','Red Rock'] else .105)
        discharges.append(dict(discharge_id=f"D{eid:05}",encounter_id=f"E{eid:05}",facility=facility,month=month,disposition=random.choice(['Home','Home health','SNF']),readmitted_30d='Y' if readmit else 'N'))
      if random.random()<.095:
        safety.append(dict(event_id=f"S{eid:05}",facility=facility,month=month,event_type=random.choice(['Medication','Fall','Pressure injury','Specimen']),severity=random.choice(['Low','Low','Moderate','High']),review_complete='Y' if random.random()>.07 else 'N'))
      eid+=1
    experience.append(dict(facility=facility,month=month,responses=round(base*.31),top_box_pct=round(76+random.random()*10-(3 if facility=='Red Rock' else 0),1)))
    refresh.append(dict(refresh_id=f"R-{facility[:2]}-{month}",facility=facility,month=month,scheduled_at=f"{month}-15 06:00",completed_at=f"{month}-15 06:{random.choice([18,23,31,54,75]):02d}",status=random.choice(['Success']*10+['Late','Failed'])))
write('encounter_extract.csv', list(encounters[0]), encounters)
write('discharge_followup.csv', list(discharges[0]), discharges)
write('safety_event_register.csv', list(safety[0]), safety)
write('experience_survey_monthly.csv', list(experience[0]), experience)
write('dashboard_refresh_log.csv', list(refresh[0]), refresh)

byfac=defaultdict(lambda: [0,0,0,0])
for x in encounters: byfac[x['facility']][0]+=1; byfac[x['facility']][1]+=x['record_complete']=='Y'
for x in discharges: byfac[x['facility']][2]+=1; byfac[x['facility']][3]+=x['readmitted_30d']=='Y'
summary=[]
for f in sorted(byfac):
  a=byfac[f]; summary.append(dict(facility=f,encounters=a[0],completeness_pct=round(100*a[1]/a[0],1),discharges=a[2],readmission_pct=round(100*a[3]/a[2],1)))
write('analysis/outputs/facility_quality_summary.csv', list(summary[0]), summary)
late=sum(1 for x in refresh if x['status']!='Success')
with (ROOT/'analysis/outputs/quality_readout.md').open('w') as f:
 f.write('# Quality reporting readout\n\n')
 f.write(f'- {len(encounters):,} synthetic encounters across 6 facilities and 12 monthly periods.\n- {late} of {len(refresh)} refreshes were late or failed.\n')
 f.write('- Focus remediation on record completeness before comparative facility reporting; this is a synthetic practice scenario, not a clinical performance assessment.\n')

def svg(path,title,labels,values,color):
 w,h=900,420; maxv=max(values); bars=[]
 for i,(lab,v) in enumerate(zip(labels,values)):
  x=80+i*130; bh=int(v/maxv*240); y=310-bh
  bars.append(f'<rect x="{x}" y="{y}" width="76" height="{bh}" rx="5" fill="{color}"/><text x="{x+38}" y="335" text-anchor="middle" font-size="13">{lab}</text><text x="{x+38}" y="{y-8}" text-anchor="middle" font-size="13">{v}%</text>')
 path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#f8fafc"/><text x="48" y="52" font-family="Arial" font-size="25" font-weight="700" fill="#0f172a">{title}</text><line x1="60" y1="310" x2="850" y2="310" stroke="#94a3b8"/> {''.join(bars)}<text x="48" y="382" font-family="Arial" font-size="13" fill="#475569">Synthetic training data • 2025 monthly reporting cycle</text></svg>''')
svg(ROOT/'docs/images/completeness_by_facility.svg','Record completeness by facility',[x['facility'].split()[0] for x in summary],[x['completeness_pct'] for x in summary],'#0f766e')
svg(ROOT/'docs/images/readmission_by_facility.svg','30-day readmission signal by facility',[x['facility'].split()[0] for x in summary],[x['readmission_pct'] for x in summary],'#c2410c')
(ROOT/'docs/images/reporting_workflow.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220"><rect width="100%" height="100%" fill="#f8fafc"/><text x="35" y="45" font-family="Arial" font-size="24" font-weight="700" fill="#0f172a">Quality reporting workflow</text><g font-family="Arial" font-size="16" fill="#fff"><rect x="45" y="90" width="190" height="62" rx="9" fill="#0f766e"/><text x="74" y="127">Source extracts</text><rect x="350" y="90" width="190" height="62" rx="9" fill="#2563eb"/><text x="377" y="127">SQL validation</text><rect x="655" y="90" width="190" height="62" rx="9" fill="#7c3aed"/><text x="683" y="127">Decision readout</text></g><path d="M245 121h90m-12-10 12 10-12 10M550 121h90m-12-10 12 10-12 10" stroke="#475569" stroke-width="3"/></svg>''')
print(f'Built {len(encounters)} encounters, {len(discharges)} discharges, and {len(safety)} safety events.')
