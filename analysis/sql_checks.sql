-- 1) Reporting-ready denominator and site-level quality metric.
SELECT site_id, COUNT(*) AS encounters,
       ROUND(100.0 * SUM(CASE WHEN record_complete = '0' OR record_valid = '0' THEN 1 ELSE 0 END) / COUNT(*), 2) AS exception_rate_pct
FROM encounters GROUP BY site_id ORDER BY exception_rate_pct DESC;

-- 2) Refresh health: failed runs or exceptions should be triaged before leadership distribution.
SELECT report_name, COUNT(*) AS runs,
       SUM(CASE WHEN run_status = 'failed' THEN 1 ELSE 0 END) AS failed_runs,
       SUM(CAST(validation_exception_count AS INTEGER)) AS validation_exceptions
FROM report_refresh_runs GROUP BY report_name;

-- 3) Demonstration-enabled self-service adoption.
SELECT month, report_name, monthly_active_users, eligible_leaders,
       ROUND(100.0 * CAST(monthly_active_users AS REAL) / eligible_leaders, 1) AS active_user_rate_pct
FROM report_adoption ORDER BY month, report_name;
