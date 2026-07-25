# Project discovery brief

## JD pain point and stakeholder workflow

An integrated health system needs analysts to turn disparate hospital, clinic, and health-plan-adjacent operational data into reliable dashboards and short decision narratives. The primary stakeholders are quality leaders, facility operations managers, data stewards, and analysts responsible for recurring reporting. Their decision is whether a facility signal is sufficiently trusted to prioritize workflow follow-up.

## Artifact decision

Selected: a Tier 2 quality-reporting readiness pack—source-style data, SQL controls, reproducible analysis, rendered evidence, and an executive readout. A dashboard-only artifact was rejected because this JD emphasizes SQL/database skills and deployed analytics; validation, definitions, and stakeholder communication are stronger evidence than a decorative interface. A generic app was rejected because it would add UI complexity without improving the reporting decision.

## Data-generating process and assumptions

The build script creates synthetic, de-identified encounter, discharge, safety-event, survey, and refresh-log records across six fictional facilities and twelve monthly periods. It intentionally introduces ordinary completeness variation and refresh exceptions so the controls have something to detect. It models analytic workflow, not clinical outcomes, and does not use patient identifiers or claim Intermountain data.

## Evidence and decision supported

The pack supports a repeatable “can we trust this signal?” decision before operations leaders consume readmission, safety, experience, or throughput indicators. It makes data quality, denominator integrity, and freshness visible alongside outcome signals.
