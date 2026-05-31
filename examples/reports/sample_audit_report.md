# Dataset Quality Audit Report

This report is generated from deterministic audit results.

## Executive Summary

- Dataset path: `examples/datasets/classification_dirty.csv`
- Test dataset path: `None`
- Target column: `label`
- Row count: 10
- Column count: 7
- Readiness score: 0/100
- Score band: `high_risk`
- Total issues: 13
- Critical: 4
- Warning: 8
- Info: 1

## Dataset Overview

| Metric | Value |
|---|---:|
| Rows | 10 |
| Columns | 7 |
| Duplicate rows | 1 |
| Duplicate percent | 0.1 |
| Target column | label |
| Mode | single_dataset |
| Audit ID | sample-audit-001 |
| Created at | 2026-05-28T00:00:00+00:00 |

## Readiness Score

Score: **0/100**

Band: **high_risk**

This score is deterministic. AI cannot modify it.

| Issue ID | Severity | Deduction | Reason |
|---|---|---:|---|
| missing_values_age_001 | warning | 8 | warning issue |
| duplicate_rows_dataset_001 | critical | 20 | critical issue |
| constant_column_constant_feature_001 | warning | 8 | warning issue |
| high_cardinality_customer_id_001 | warning | 8 | warning issue |
| high_cardinality_city_001 | warning | 8 | warning issue |
| high_cardinality_signup_date_001 | warning | 8 | warning issue |
| class_imbalance_label_001 | warning | 8 | warning issue |
| id_like_customer_id_001 | info | 4 | info issue; requires human review |
| outlier_risk_age_001 | warning | 8 | warning issue |
| outlier_risk_income_text_001 | warning | 8 | warning issue |
| target_leakage_candidate_customer_id_category_target_mapping_001 | critical | 22 | critical issue; requires human review |
| target_leakage_candidate_income_text_target_correlation_001 | critical | 22 | critical issue; requires human review |
| target_leakage_candidate_signup_date_category_target_mapping_001 | critical | 22 | critical issue; requires human review |

## Issue Summary

### Critical

- `duplicate_rows_dataset_001`: Duplicate rows detected
  - Affected column: `None`
  - Evidence metric: `duplicate_row_percent`
  - Observed value: 0.1
  - Threshold: 0.1
  - Recommendation: Investigate duplicate records and decide whether they represent valid repeated observations before training.
  - Human review required: False

- `target_leakage_candidate_customer_id_category_target_mapping_001`: Target leakage candidate detected
  - Affected column: `customer_id`
  - Evidence metric: `leakage_candidate_signal`
  - Observed value: 1
  - Threshold: 0.98
  - Recommendation: Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event.
  - Human review required: True

- `target_leakage_candidate_income_text_target_correlation_001`: Target leakage candidate detected
  - Affected column: `income_text`
  - Evidence metric: `leakage_candidate_signal`
  - Observed value: 0.9966
  - Threshold: 0.95
  - Recommendation: Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event.
  - Human review required: True

- `target_leakage_candidate_signup_date_category_target_mapping_001`: Target leakage candidate detected
  - Affected column: `signup_date`
  - Evidence metric: `leakage_candidate_signal`
  - Observed value: 1
  - Threshold: 0.98
  - Recommendation: Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event.
  - Human review required: True

### Warning

- `missing_values_age_001`: Missing values detected in feature column
  - Affected column: `age`
  - Evidence metric: `missing_percent`
  - Observed value: 0.2
  - Threshold: 0.1
  - Recommendation: Handle missing values inside the preprocessing pipeline fitted only on training data.
  - Human review required: False

- `constant_column_constant_feature_001`: Constant feature column detected
  - Affected column: `constant_feature`
  - Evidence metric: `unique_count`
  - Observed value: 1
  - Threshold: 1
  - Recommendation: Remove or ignore constant feature columns during modeling.
  - Human review required: False

- `high_cardinality_customer_id_001`: High-cardinality categorical column detected
  - Affected column: `customer_id`
  - Evidence metric: `unique_percent`
  - Observed value: 0.9
  - Threshold: 0.5
  - Recommendation: Confirm whether this column is an identifier or a usable model feature before training.
  - Human review required: False

- `high_cardinality_city_001`: High-cardinality categorical column detected
  - Affected column: `city`
  - Evidence metric: `unique_percent`
  - Observed value: 0.5
  - Threshold: 0.5
  - Recommendation: Confirm whether this column is an identifier or a usable model feature before training.
  - Human review required: False

- `high_cardinality_signup_date_001`: High-cardinality categorical column detected
  - Affected column: `signup_date`
  - Evidence metric: `unique_percent`
  - Observed value: 0.8
  - Threshold: 0.5
  - Recommendation: Confirm whether this column is an identifier or a usable model feature before training.
  - Human review required: False

- `class_imbalance_label_001`: Target class imbalance detected
  - Affected column: `label`
  - Evidence metric: `dominant_class_ratio`
  - Observed value: 0.9
  - Threshold: 0.8
  - Recommendation: Use stratified validation and consider class-aware metrics, sampling, or weighting in the training pipeline.
  - Human review required: False

- `outlier_risk_age_001`: Numeric outlier risk detected
  - Affected column: `age`
  - Evidence metric: `outlier_percent`
  - Observed value: 0.1
  - Threshold: 0.05
  - Recommendation: Inspect outliers before training and consider robust preprocessing where appropriate; do not blindly remove them.
  - Human review required: False

- `outlier_risk_income_text_001`: Numeric outlier risk detected
  - Affected column: `income_text`
  - Evidence metric: `outlier_percent`
  - Observed value: 0.1
  - Threshold: 0.05
  - Recommendation: Inspect outliers before training and consider robust preprocessing where appropriate; do not blindly remove them.
  - Human review required: False

### Info

- `id_like_customer_id_001`: Suspicious ID-like column detected
  - Affected column: `customer_id`
  - Evidence metric: `unique_percent`
  - Observed value: 0.9
  - Threshold: 0.95
  - Recommendation: Confirm whether this column is an ID and whether it is available at prediction time.
  - Human review required: True

## Column Overview

| Column | Role | Type | Missing % | Unique % | Numeric | Categorical |
|---|---|---|---:|---:|---|---|
| customer_id | feature | str | 0 | 0.9 | False | True |
| age | feature | float64 | 0.2 | 0.6 | True | False |
| income_text | feature | int64 | 0 | 0.8 | True | False |
| city | feature | str | 0 | 0.5 | False | True |
| signup_date | datetime_candidate | str | 0 | 0.8 | False | True |
| constant_feature | feature | str | 0 | 0.1 | False | True |
| label | target | int64 | 0 | 0.2 | True | False |

## Recommended Next Steps

- Handle missing values inside the preprocessing pipeline fitted only on training data.
- Investigate duplicate records and decide whether they represent valid repeated observations before training.
- Remove or ignore constant feature columns during modeling.
- Confirm whether this column is an identifier or a usable model feature before training.
- Use stratified validation and consider class-aware metrics, sampling, or weighting in the training pipeline.
- Confirm whether this column is an ID and whether it is available at prediction time.
- Inspect outliers before training and consider robust preprocessing where appropriate; do not blindly remove them.
- Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event.

## Reproducibility Metadata

- Package version: `0.2.0`
- Engine version: `0.1.0`
- Deterministic: `True`
- AI generated: `False`
