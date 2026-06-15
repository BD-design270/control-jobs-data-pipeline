from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "control_jobs.csv"
DATABASE_FILE = PROJECT_ROOT / "data" / "control_jobs.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
SUMMARY_FILE = OUTPUT_DIR / "control_job_daily_summary.csv"

SQL_FILES = [
    PROJECT_ROOT / "sql" / "create_tables.sql",
    PROJECT_ROOT / "sql" / "create_view.sql",
    PROJECT_ROOT / "sql" / "build_summary.sql",
]


def execute_sql_file(
    connection: sqlite3.Connection,
    sql_file: Path,
) -> None:
    sql = sql_file.read_text(encoding="utf-8")
    connection.executescript(sql)
    print(f"Executed: {sql_file.name}")


def load_source_data(
    connection: sqlite3.Connection,
) -> int:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Source data is missing. Run "
            "'python src/generate_data.py' first."
        )

    data = pd.read_csv(DATA_FILE)

    data.to_sql(
        "raw_control_jobs",
        connection,
        if_exists="append",
        index=False,
    )

    return len(data)


def export_summary(
    connection: sqlite3.Connection,
) -> int:
    summary = pd.read_sql_query(
        """
        SELECT *
        FROM control_job_daily_summary
        ORDER BY run_date, business_area
        """,
        connection,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_FILE, index=False)

    return len(summary)


def main() -> None:
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_FILE) as connection:
        execute_sql_file(connection, SQL_FILES[0])

        loaded_rows = load_source_data(connection)

        execute_sql_file(connection, SQL_FILES[1])
        execute_sql_file(connection, SQL_FILES[2])

        summary_rows = export_summary(connection)

    print(f"Loaded {loaded_rows:,} job records.")
    print(f"Created {summary_rows:,} summary records.")
    print(f"Database created: {DATABASE_FILE}")
    print(f"Summary exported: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
