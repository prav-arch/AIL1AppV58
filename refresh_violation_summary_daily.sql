-- Drop the view if it exists (works for tables/views in 18.x)
DROP TABLE IF EXISTS l1_app_db.violation_summary_daily;

-- Create the view with per-day, per-table severity breakdown
CREATE VIEW l1_app_db.violation_summary_daily AS
SELECT *
FROM
(
    SELECT
        toDate(event_time) AS day,
        'fh_violations' AS table_name,
        sum(severity = 4) AS critical_count,     -- 'critical'
        sum(severity = 3) AS high_count,         -- 'high' or 'major'
        sum(severity = 1) AS warning_count,      -- 'warning'
        (sum(severity = 4) + sum(severity = 3) + sum(severity = 1)) AS total_critical_high_warning
    FROM l1_app_db.fh_violations
    GROUP BY day

    UNION ALL

    SELECT
        toDate(event_time) AS day,
        'cp_up_coupling' AS table_name,
        sum(severity = 4) AS critical_count,
        sum(severity = 3) AS high_count,
        sum(severity = 1) AS warning_count,
        (sum(severity = 4) + sum(severity = 3) + sum(severity = 1)) AS total_critical_high_warning
    FROM l1_app_db.cp_up_coupling
    GROUP BY day

    UNION ALL

    SELECT
        toDate(event_time) AS day,
        'interference_splane' AS table_name,
        sum(severity = 4) AS critical_count,
        sum(severity = 3) AS high_count,
        sum(severity = 1) AS warning_count,
        (sum(severity = 4) + sum(severity = 3) + sum(severity = 1)) AS total_critical_high_warning
    FROM l1_app_db.interference_splane
    GROUP BY day
)
ORDER BY day DESC, table_name;

-- Show the summary output
SELECT * FROM l1_app_db.violation_summary_daily ORDER BY day DESC, table_name;
