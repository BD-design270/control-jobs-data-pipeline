DROP TABLE IF EXISTS control_job_daily_summary;

CREATE TABLE control_job_daily_summary AS
SELECT
    run_date,
    business_area,
    COUNT(*) AS total_jobs,
    SUM(success_flag) AS successful_jobs,
    SUM(failure_flag) AS failed_jobs,
    SUM(sla_breach_flag) AS sla_breaches,
    SUM(records_processed) AS total_records_processed,
    ROUND(AVG(processing_seconds), 2) AS average_processing_seconds,
    ROUND(
        100.0 * SUM(success_flag) / COUNT(*),
        2
    ) AS success_rate_percent
FROM vw_control_job_status
GROUP BY
    run_date,
    business_area;
