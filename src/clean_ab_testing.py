from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "ab_testing_large.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = PROCESSED_DIR / "ab_testing_analysis_ready.csv"


def clean_ab(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("%", "pct", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    missing_id = df["user_id"].isna()
    if missing_id.any():
        df.loc[missing_id, "user_id"] = [f"U_MISSING_{i:04d}" for i in range(1, int(missing_id.sum()) + 1)]

    for col in ["variant", "device_type", "country"]:
        df[col] = df[col].fillna("Unknown").astype(str)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df["conversion"] = pd.to_numeric(df["conversion"], errors="coerce").round().clip(0, 1)
    df["conversion"] = df["conversion"].fillna(0)

    for col in ["click_count", "page_load_time_ms", "session_length_s", "revenue_usd", "bounce_rate_pct"]:
        series = pd.to_numeric(df[col], errors="coerce")
        df[col] = series.fillna(series.median())

    df = df.drop_duplicates(subset=["user_id"], keep="first").reset_index(drop=True)
    df["conversion_label"] = df["conversion"].map({0.0: "No conversion", 1.0: "Converted"})
    return df


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    cleaned = clean_ab(raw)
    cleaned.to_csv(OUTPUT, index=False)
    print(f"raw rows: {len(raw)}")
    print(f"analysis-ready rows: {len(cleaned)}")
    print(f"saved: {OUTPUT}")
    print(cleaned.groupby("variant")["conversion"].mean())


if __name__ == "__main__":
    main()
