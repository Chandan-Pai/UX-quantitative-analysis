from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "usability_testing_large.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = PROCESSED_DIR / "usability_testing_analysis_ready.csv"


def clean_usability(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("%", "pct", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    missing_id = df["participant_id"].isna()
    if missing_id.any():
        df.loc[missing_id, "participant_id"] = [
            f"P_MISSING_{i:04d}" for i in range(1, int(missing_id.sum()) + 1)
        ]

    for col in ["task_name", "device_type", "moderator", "error_type"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    df["task_success"] = pd.to_numeric(df["task_success"], errors="coerce").round().clip(0, 1)
    df["task_success"] = df["task_success"].fillna(df["task_success"].mode(dropna=True).iloc[0])

    for col, low, high in [
        ("completion_time_s", 1, None),
        ("error_count", 0, None),
        ("frustration_level", 1, 7),
        ("help_requested", 0, 1),
        ("satisfaction_score", 1, 7),
    ]:
        series = pd.to_numeric(df[col], errors="coerce")
        if low is not None:
            series = series.mask(series < low)
        if high is not None:
            series = series.mask(series > high)
        df[col] = series.fillna(series.median())

    df["help_requested"] = df["help_requested"].round().clip(0, 1)
    df = df.drop_duplicates(subset=["participant_id", "task_name"], keep="first").reset_index(drop=True)
    df["task_success_label"] = df["task_success"].map({0.0: "Failed", 1.0: "Completed"})
    return df


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    cleaned = clean_usability(raw)
    cleaned.to_csv(OUTPUT, index=False)
    print(f"raw rows: {len(raw)}")
    print(f"analysis-ready rows: {len(cleaned)}")
    print(f"saved: {OUTPUT}")


if __name__ == "__main__":
    main()
