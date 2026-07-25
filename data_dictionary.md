# Data Dictionary

All source-style tables are synthetic and de-identified. They model the reporting grain a health-system analytics team might use; no clinical decisions should be made from this data.

| Table | Grain | Selected fields | Purpose |
|---|---|---|---|
| `encounters.csv` | encounter | service line, length of stay, 30-day readmission flag, completeness/validity flags | Quality, utilization, and data-integrity denominators |
| `data_quality_events.csv` | site/event/day | issue type, severity, records affected, reporting hold | Remediation workflow and escalation evidence |
| `report_refresh_runs.csv` | report refresh | run status, duration, validation exceptions | Reporting operational reliability |
| `report_adoption.csv` | report/month | eligible leaders, monthly active users, demo attendance | Self-service enablement and training uptake |

The generated encounter key is a non-identifying synthetic key. Site IDs represent fictional reporting units.
