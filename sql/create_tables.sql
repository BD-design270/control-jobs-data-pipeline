DROP TABLE IF EXISTS raw_control_jobs;

CREATE TABLE raw_control_jobs (
    job_id TEXT PRIMARY KEY,
    control_id TEXT NOT NULL,
    business_area TEXT NOT NULL,
    run_date TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER NOT NULL,
    processing_seconds INTEGER NOT NULL,
    failure_reason TEXT,
    sla_breach_flag INTEGER NOT NULL
);
