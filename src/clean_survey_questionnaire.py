from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "survey_questionnaire_large.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CLEANED = PROCESSED_DIR / "survey_questionnaire_cleaned.csv"
OUTPUT_ANALYSIS_READY = PROCESSED_DIR / "survey_questionnaire_analysis_ready.csv"


def _fill_unknown(series: pd.Series) -> pd.Series:
    return series.fillna("Unknown")


def _impute_numeric(series: pd.Series, low: float | None = None, high: float | None = None) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if low is not None:
        numeric = numeric.mask(numeric < low)
    if high is not None:
        numeric = numeric.mask(numeric > high)
    median = numeric.dropna().median()
    if pd.isna(median):
        return numeric
    return numeric.fillna(median)


def clean_survey_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    missing_id = df["Participant_ID"].isna()
    if missing_id.any():
        df.loc[missing_id, "Participant_ID"] = [f"P_MISSING_{i:04d}" for i in range(1, missing_id.sum() + 1)]

    for column in ["Gender", "Device_Type", "Experience_Level"]:
        df[column] = _fill_unknown(df[column])

    df["Age"] = _impute_numeric(df["Age"], 18, 75).clip(18, 75)
    df["Completion_Time_s"] = pd.to_numeric(df["Completion_Time_s"], errors="coerce")
    df["Completion_Time_s"] = df["Completion_Time_s"].mask(df["Completion_Time_s"] <= 0)
    df["Completion_Time_s"] = df["Completion_Time_s"].fillna(df["Completion_Time_s"].dropna().median())

    binary_columns = ["Task_Success", "Attention_Check_Passed"]
    for column in binary_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").round().clip(0, 1)
        df[column] = df[column].fillna(df[column].mode(dropna=True).iloc[0])

    likert_1_5 = [f"SUS_Q{i}" for i in range(1, 11)]
    for column in likert_1_5:
        df[column] = _impute_numeric(df[column], 1, 5).round().clip(1, 5)

    for column in ["UEQ_Attractiveness", "UEQ_Efficiency", "UEQ_Perspicuity"]:
        df[column] = _impute_numeric(df[column], 1, 7).round().clip(1, 7)

    for column in ["NASA_TLX_Mental", "NASA_TLX_Temporal", "NASA_TLX_Frustration"]:
        df[column] = _impute_numeric(df[column], 0, 21).clip(0, 21)

    for column in ["Trust_Score", "Ease_of_Use", "Willingness_to_Reuse"]:
        df[column] = _impute_numeric(df[column], 1, 7).clip(1, 7)

    df = df.drop_duplicates().reset_index(drop=True)
    return df


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    cleaned = clean_survey_data(raw)

    cleaned.to_csv(OUTPUT_CLEANED, index=False)
    analysis_ready = cleaned[cleaned["Attention_Check_Passed"] == 1].copy()
    analysis_ready.to_csv(OUTPUT_ANALYSIS_READY, index=False)

    print(f"raw rows: {len(raw)}")
    print(f"cleaned rows: {len(cleaned)}")
    print(f"analysis-ready rows: {len(analysis_ready)}")
    print(f"saved: {OUTPUT_CLEANED}")
    print(f"saved: {OUTPUT_ANALYSIS_READY}")


if __name__ == "__main__":
    main()