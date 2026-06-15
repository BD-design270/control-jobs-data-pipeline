DROP VIEW IF EXISTS vw_control_job_status;

CREATE VIEW vw_control_job_status AS
SELECT
    job_id,
    control_id,
    business_area,
    DATE(run_date) AS run_date,
    UPPER(TRIM(status)) AS status,
    records_processed,
    processing_seconds,
    failure_reason,

    CASE
        WHEN UPPER(TRIM(status)) = 'SUCCESS' THEN 1
        ELSE 0
    END AS success_flag,

    CASE
        WHEN UPPER(TRIM(status)) = 'FAILED' THEN 1
        ELSE 0
    END AS failure_flag,

    CASE
        WHEN processing_seconds > 300 THEN 1
        ELSE 0
    END AS sla_breach_flag

FROM raw_control_jobs;
