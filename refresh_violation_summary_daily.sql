-- Drop the view if it exists
DROP VIEW IF EXISTS l1_app_db.violation_summary_daily;

-- Create the view with per-day, per-table severity breakdown
CREATE VIEW l1_app_db.violation_summary_daily AS
SELECT *
FROM
(
    SELECT
        toDate(event_time) AS day,
        'fh_violations' AS table_name,
        sum(severity = 'critical') AS critical_count,
        sum(severity = 'high') AS high_count,
        sum(severity = 'warning') AS warning_count,
        (sum(severity = 'critical') + sum(severity = 'high') + sum(severity = 'warning')) AS total_critical_high_warning
    FROM l1_app_db.fh_violations
    GROUP BY day

    UNION ALL

    SELECT
        toDate(event_time) AS day,
        'cp_up_coupling' AS table_name,
        sum(severity = 'critical') AS critical_count,
        sum(severity = 'high') AS high_count,
        sum(severity = 'warning') AS warning_count,
        (sum(severity = 'critical') + sum(severity = 'high') + sum(severity = 'warning')) AS total_critical_high_warning
    FROM l1_app_db.cp_up_coupling
    GROUP BY day

    UNION ALL

    SELECT
        toDate(event_time) AS day,
        'interference_splane' AS table_name,
        sum(severity = 'critical') AS critical_count,
        sum(severity = 'high') AS high_count,
        sum(severity = 'warning') AS warning_count,
        (sum(severity = 'critical') + sum(severity = 'high') + sum(severity = 'warning')) AS total_critical_high_warning
    FROM l1_app_db.interference_splane
    GROUP BY day
)
ORDER BY day DESC, table_name;

-- Show the summary output
SELECT * FROM l1_app_db.violation_summary_daily ORDER BY day DESC, table_name;
