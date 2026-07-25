#!/usr/bin/env python3
"""Generate a synthetic, de-identified hospital reporting-readiness dataset and evidence."""
from __future__ import annotations

import csv
import random
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis" / "outputs"
IMG = ROOT / "docs" / "images"
random.seed(41)

REGIONS = ["North", "Central", "South", "Urban", "Mountain"]
SERVICE_LINES = ["Medicine", "Surgery", "Cardiology", "Orthopedics"]
SITES = [(f"H{i:02d}", REGIONS[i % 5], SERVICE_LINES[i % 4]) for i in range(1, 21)]

def write_csv(name, fields, rows):
    with (DATA / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    DATA.mkdir(exist_ok=True); OUT.mkdir(parents=True, exist_ok=True); IMG.mkdir(parents=True, exist_ok=True)
    encounters, quality_events, refresh_runs, adoption = [], [], [], []
    start = date(2025, 1, 1)
    for day_n in range(180):
        day = start + timedelta(days=day_n)
        for site_id, region, line in SITES:
            base = 24 + (hash(site_id) % 10)
            for n in range(base + random.randrange(-5, 7)):
                los = max(1, round(random.gauss(4.5 if line == "Medicine" else 3.3, 1.5), 1))
                readmit = int(random.random() < (0.128 if line == "Medicine" else 0.083))
                complete = int(random.random() > (0.018 + (0.015 if site_id in {"H03", "H12"} else 0)))
                valid = int(random.random() > (0.011 + (0.012 if site_id == "H07" else 0)))
                encounters.append({"encounter_id": f"E{day_n:03d}{site_id}{n:03d}", "encounter_date": day.isoformat(), "site_id":site_id, "region":region, "service_line":line, "length_of_stay_days":los, "readmitted_30d":readmit, "cost_per_encounter":round(random.gauss(10750 + 650*readmit, 1200),2), "record_complete":complete, "record_valid":valid})
        for site_id, region, line in SITES:
            if day_n % 3 == 0:
                issue = random.choice(["late_feed", "duplicate_key", "missing_discharge", "invalid_code"])
                quality_events.append({"event_id":f"Q{day_n:03d}{site_id}","event_date":day.isoformat(),"site_id":site_id,"region":region,"issue_type":issue,"severity":random.choice(["low","medium","high"]),"records_affected":random.randrange(4,75),"resolved_hours":round(random.uniform(2,42),1),"reporting_hold":int(issue in ["duplicate_key","missing_discharge"] and random.random()<.45)})
        for report in ["Quality & Safety", "Care Utilization", "Operations Flow"]:
            refresh_runs.append({"run_id":f"R{day_n:03d}{report[:2]}","run_date":day.isoformat(),"report_name":report,"source_system":random.choice(["EHR","ADT","Finance mart"]),"run_status":"success" if random.random()>.055 else "failed","duration_minutes":round(random.uniform(6,38),1),"validation_exception_count":random.randrange(0,8)})
    for month in range(1,7):
        for report in ["Quality & Safety", "Care Utilization", "Operations Flow"]:
            adoption.append({"month":f"2025-{month:02d}","report_name":report,"eligible_leaders":48,"monthly_active_users":random.randrange(27,45),"guided_demo_attendees":random.randrange(8,25),"self_service_sessions":random.randrange(100,310)})
    write_csv("encounters.csv", list(encounters[0]), encounters)
    write_csv("data_quality_events.csv", list(quality_events[0]), quality_events)
    write_csv("report_refresh_runs.csv", list(refresh_runs[0]), refresh_runs)
    write_csv("report_adoption.csv", list(adoption[0]), adoption)
    con = sqlite3.connect(OUT / "readiness_analysis.sqlite")
    for name in ["encounters","data_quality_events","report_refresh_runs","report_adoption"]:
        con.execute(f"DROP TABLE IF EXISTS {name}")
        rows = list(csv.DictReader((DATA / f"{name}.csv").open()))
        cols = rows[0].keys(); con.execute(f"CREATE TABLE {name} ({','.join(c+' TEXT' for c in cols)})")
        con.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in cols)})", [[r[c] for c in cols] for r in rows])
    con.commit()
    metrics = defaultdict(lambda: [0,0,0,0.0])
    for r in encounters:
        x=metrics[r['site_id']]; x[0]+=1; x[1]+=r['readmitted_30d']; x[2]+=int(not (r['record_complete'] and r['record_valid'])); x[3]+=r['length_of_stay_days']
    # corrected structured output without exposing individual health data
    summary=[]
    for site, (count, readm, dq, los) in metrics.items():
        summary.append({"site_id":site,"encounters":count,"readmission_rate_pct":round(100*readm/count,2),"data_quality_exception_rate_pct":round(100*dq/count,2),"avg_length_of_stay_days":round(los/count,2)})
    summary.sort(key=lambda r:(-r['data_quality_exception_rate_pct'],-r['readmission_rate_pct']))
    with (OUT / "site_readiness_priority.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    # Charts
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax=plt.subplots(figsize=(10,5)); top=summary[:10]
    ax.bar([x['site_id'] for x in top],[x['data_quality_exception_rate_pct'] for x in top],color="#b91c1c"); ax.axhline(2.5,color="#0f766e",ls="--",label="2.5% readiness threshold"); ax.set_ylabel("Exception rate (%)"); ax.set_title("Sites prioritized for reporting-data remediation"); ax.legend(); fig.tight_layout();fig.savefig(IMG / "quality-exceptions-by-site.png",dpi=170);plt.close(fig)
    months=sorted({r['month'] for r in adoption}); values=[]
    for month in months: values.append(sum(int(r['monthly_active_users']) for r in adoption if r['month']==month)/sum(int(r['eligible_leaders']) for r in adoption if r['month']==month)*100)
    fig,ax=plt.subplots(figsize=(10,5));ax.plot(months,values,marker="o",color="#0f766e",lw=3);ax.set_ylim(0,100);ax.set_ylabel("Leadership active-user rate (%)");ax.set_title("Self-service reporting adoption after recurring demos");fig.tight_layout();fig.savefig(IMG / "self-service-adoption-trend.png",dpi=170);plt.close(fig)
    with (OUT / "reporting_readiness_scorecard.csv").open("w",newline="") as f:
        rows=[{"metric":"Synthetic encounters analyzed","value":len(encounters),"decision_use":"Denominator for quality and utilization monitoring"},{"metric":"Reporting refresh runs","value":len(refresh_runs),"decision_use":"Monitor refresh reliability and exceptions"},{"metric":"Data-quality events","value":len(quality_events),"decision_use":"Route remediation queue to data owners"},{"metric":"Priority sites","value":10,"decision_use":"Start validation huddles with highest exception rates"}]
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    con.close()

if __name__ == "__main__": main()
