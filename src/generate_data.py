from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
NUMBER_OF_JOBS = 1_200

OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "control_jobs.csv"


def generate_control_jobs(number_of_jobs: int) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    business_areas = [
        "Customer Operations",
        "Payments",
        "Financial Crime",
        "Lending",
        "Regulatory Reporting",
    ]

    statuses = ["SUCCESS", "FAILED", "WARNING"]

    run_dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=30,
        freq="D",
    )

    status_values = rng.choice(
        statuses,
        size=number_of_jobs,
        p=[0.88, 0.07, 0.05],
    )

    processing_seconds = rng.integers(
        low=20,
        high=600,
        size=number_of_jobs,
    )

    records_processed = rng.integers(
        low=100,
        high=500_000,
        size=number_of_jobs,
    )

    failure_reasons = {
        "SUCCESS": None,
        "WARNING": "Processing time exceeded expected threshold",
        "FAILED": None,
    }

    failed_reasons = rng.choice(
        [
            "Source data unavailable",
            "Schema validation failed",
            "Duplicate records detected",
            "Record-count reconciliation failed",
            "Pipeline timeout",
        ],
        size=number_of_jobs,
    )

    data = pd.DataFrame(
        {
            "job_id": [
                f"JOB-{number:05d}"
                for number in range(1, number_of_jobs + 1)
            ],
            "control_id": [
                f"CTRL-{number:04d}"
                for number in rng.integers(1, 251, number_of_jobs)
            ],
            "business_area": rng.choice(
                business_areas,
                size=number_of_jobs,
            ),
            "run_date": rng.choice(
                run_dates,
                size=number_of_jobs,
            ),
            "status": status_values,
            "records_processed": records_processed,
            "processing_seconds": processing_seconds,
        }
    )

    data["failure_reason"] = [
        failed_reasons[index]
        if status == "FAILED"
        else failure_reasons[status]
        for index, status in enumerate(data["status"])
    ]

    data["sla_breach_flag"] = (
        data["processing_seconds"] > 300
    ).astype(int)

    return data.sort_values(
        by=["run_date", "job_id"]
    ).reset_index(drop=True)


def validate_generated_data(data: pd.DataFrame) -> None:
    if len(data) < 1_000:
        raise ValueError("At least 1,000 job records are required.")

    if data["job_id"].duplicated().any():
        raise ValueError("Duplicate job IDs were generated.")

    if data["control_id"].isna().any():
        raise ValueError("Control ID cannot be empty.")

    valid_statuses = {"SUCCESS", "FAILED", "WARNING"}

    if not set(data["status"]).issubset(valid_statuses):
        raise ValueError("Invalid job status detected.")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = generate_control_jobs(NUMBER_OF_JOBS)
    validate_generated_data(data)

    data.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(data):,} synthetic job records.")
    print(f"Output saved to: {OUTPUT_FILE}")
    print("\nStatus summary:")
    print(data["status"].value_counts())


if __name__ == "__main__":
    main()
