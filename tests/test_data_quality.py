from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "data" / "control_jobs.db"


def read_query(query: str) -> pd.DataFrame:
    with sqlite3.connect(DATABASE_FILE) as connection:
        return pd.read_sql_query(query, connection)


def test_database_exists():
    assert DATABASE_FILE.exists()


def test_at_least_1000_jobs_loaded():
    result = read_query(
        "SELECT COUNT(*) AS row_count FROM raw_control_jobs"
    )
    assert result.loc[0, "row_count"] >= 1000


def test_job_ids_are_unique():
    result = read_query(
        """
        SELECT COUNT(*) AS total,
               COUNT(DISTINCT job_id) AS unique_jobs
        FROM raw_control_jobs
        """
    )
    assert result.loc[0, "total"] == result.loc[0, "unique_jobs"]


def test_control_ids_are_not_null():
    result = read_query(
        """
        SELECT COUNT(*) AS null_count
        FROM raw_control_jobs
        WHERE control_id IS NULL
        """
    )
    assert result.loc[0, "null_count"] == 0


def test_status_values_are_valid():
    result = read_query(
        """
        SELECT DISTINCT status
        FROM raw_control_jobs
        """
    )
    assert set(result["status"]) <= {
        "SUCCESS",
        "FAILED",
        "WARNING",
    }


def test_failed_jobs_have_failure_reason():
    result = read_query(
        """
        SELECT COUNT(*) AS invalid_count
        FROM raw_control_jobs
        WHERE status = 'FAILED'
          AND (
              failure_reason IS NULL
              OR TRIM(failure_reason) = ''
          )
        """
    )
    assert result.loc[0, "invalid_count"] == 0


def test_summary_success_rate_is_valid():
    result = read_query(
        """
        SELECT COUNT(*) AS invalid_count
        FROM control_job_daily_summary
        WHERE success_rate_percent < 0
           OR success_rate_percent > 100
        """
    )
    assert result.loc[0, "invalid_count"] == 0
