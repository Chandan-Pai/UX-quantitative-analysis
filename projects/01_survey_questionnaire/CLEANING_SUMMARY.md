# Survey Cleaning Summary

## Raw Dataset
- Rows: 1000
- Columns: 27
- Source: UX_datasets-main/datasets_by_type/01_survey_questionnaire/large/survey_questionnaire_large.csv

## Observed Data Issues
- Missing Participant_ID values
- Missing demographic and experience labels
- Missing Likert-scale and metric values
- Out-of-range values in several survey and UX metric columns
- Negative values in NASA_TLX_Frustration
- Zero or invalid completion-time values

## Cleaning Rules Applied
- Filled missing Participant_ID values with generated placeholder IDs
- Filled missing categorical values with `Unknown`
- Imputed numeric missing values using the median after validating ranges
- Corrected invalid ranges for:
  - Age
  - SUS items
  - UEQ metrics
  - NASA-TLX metrics
  - Trust / Ease_of_Use / Willingness_to_Reuse
  - Task_Success and Attention_Check_Passed
- Replaced non-positive completion times with median positive completion time
- Removed duplicate rows

## Outputs
- Cleaned dataset: ../data/processed/survey_questionnaire_cleaned.csv
- Analysis-ready dataset: ../data/processed/survey_questionnaire_analysis_ready.csv

## Final Counts
- Cleaned rows: 1000
- Analysis-ready rows after attention-check filter: 883
