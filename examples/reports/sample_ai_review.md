# AI-Assisted Dataset Review

This AI-assisted review is generated from deterministic audit findings.

## Readiness

- Readiness score: 0/100
- Score band: high_risk
- Audit ID: sample-audit-001

## Priority Summary

- High priority: 4
- Medium priority: 8
- Low priority: 1

## Prioritized Issues

- `duplicate_rows_dataset_001`: high priority (critical, duplicate_rows) - Duplicate rows detected was reported by the deterministic audit with critical severity.
- `target_leakage_candidate_customer_id_category_target_mapping_001`: high priority (critical, target_leakage_candidate) - Target leakage candidate detected was reported by the deterministic audit with critical severity.
- `target_leakage_candidate_income_text_target_correlation_001`: high priority (critical, target_leakage_candidate) - Target leakage candidate detected was reported by the deterministic audit with critical severity.
- `target_leakage_candidate_signup_date_category_target_mapping_001`: high priority (critical, target_leakage_candidate) - Target leakage candidate detected was reported by the deterministic audit with critical severity.
- `missing_values_age_001`: medium priority (warning, missing_values) - Missing values detected in feature column was reported by the deterministic audit with warning severity.
- `constant_column_constant_feature_001`: medium priority (warning, constant_columns) - Constant feature column detected was reported by the deterministic audit with warning severity.
- `high_cardinality_customer_id_001`: medium priority (warning, high_cardinality) - High-cardinality categorical column detected was reported by the deterministic audit with warning severity.
- `high_cardinality_city_001`: medium priority (warning, high_cardinality) - High-cardinality categorical column detected was reported by the deterministic audit with warning severity.
- `high_cardinality_signup_date_001`: medium priority (warning, high_cardinality) - High-cardinality categorical column detected was reported by the deterministic audit with warning severity.
- `class_imbalance_label_001`: medium priority (warning, class_imbalance) - Target class imbalance detected was reported by the deterministic audit with warning severity.
- `outlier_risk_age_001`: medium priority (warning, outlier_risk) - Numeric outlier risk detected was reported by the deterministic audit with warning severity.
- `outlier_risk_income_text_001`: medium priority (warning, outlier_risk) - Numeric outlier risk detected was reported by the deterministic audit with warning severity.
- `id_like_customer_id_001`: low priority (info, id_like_columns) - Suspicious ID-like column detected was reported by the deterministic audit with info severity.

## Safe Next Steps

- `duplicate_rows_dataset_001`: Investigate duplicate records and decide whether they represent valid repeated observations before training. (safe_suggestion_only)
- `target_leakage_candidate_customer_id_category_target_mapping_001`: Manually review this finding before changing training data or pipeline behavior. Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event. (manual_review)
- `target_leakage_candidate_income_text_target_correlation_001`: Manually review this finding before changing training data or pipeline behavior. Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event. (manual_review)
- `target_leakage_candidate_signup_date_category_target_mapping_001`: Manually review this finding before changing training data or pipeline behavior. Confirm whether this feature is available at prediction time; remove it from training if it is derived from or created after the target event. (manual_review)
- `missing_values_age_001`: Handle missing values inside the preprocessing pipeline fitted only on training data. (safe_suggestion_only)
- `constant_column_constant_feature_001`: Remove or ignore constant feature columns during modeling. (safe_suggestion_only)
- `high_cardinality_customer_id_001`: Confirm whether this column is an identifier or a usable model feature before training. (safe_suggestion_only)
- `high_cardinality_city_001`: Confirm whether this column is an identifier or a usable model feature before training. (safe_suggestion_only)
- `high_cardinality_signup_date_001`: Confirm whether this column is an identifier or a usable model feature before training. (safe_suggestion_only)
- `class_imbalance_label_001`: Use stratified validation and consider class-aware metrics, sampling, or weighting in the training pipeline. (safe_suggestion_only)
- `outlier_risk_age_001`: Inspect outliers before training and consider robust preprocessing where appropriate; do not blindly remove them. (safe_suggestion_only)
- `outlier_risk_income_text_001`: Inspect outliers before training and consider robust preprocessing where appropriate; do not blindly remove them. (safe_suggestion_only)
- `id_like_customer_id_001`: Manually review this finding before changing training data or pipeline behavior. Confirm whether this column is an ID and whether it is available at prediction time. (manual_review)

## Human Review Questions

- `target_leakage_candidate_customer_id_category_target_mapping_001`: Is this column or condition valid, available at prediction time, and appropriate for model training? Reason: A target leakage candidate can inflate training and validation metrics if the feature is derived from the target event.
- `target_leakage_candidate_income_text_target_correlation_001`: Is this column or condition valid, available at prediction time, and appropriate for model training? Reason: A target leakage candidate can inflate training and validation metrics if the feature is derived from the target event.
- `target_leakage_candidate_signup_date_category_target_mapping_001`: Is this column or condition valid, available at prediction time, and appropriate for model training? Reason: A target leakage candidate can inflate training and validation metrics if the feature is derived from the target event.
- `id_like_customer_id_001`: Is this column or condition valid, available at prediction time, and appropriate for model training? Reason: ID-like columns may create leakage or brittle memorization if they are not available or meaningful at prediction time.

## Contract Advice

- `missing_values_age_001`: max_missing_percent_review for `age` - Review whether the data contract should encode this deterministic finding as an explicit validation rule.
- `id_like_customer_id_001`: uniqueness_or_id_role_review for `customer_id` - Review whether the data contract should encode this deterministic finding as an explicit validation rule.
- `outlier_risk_age_001`: numeric_range_review for `age` - Review whether the data contract should encode this deterministic finding as an explicit validation rule.
- `outlier_risk_income_text_001`: numeric_range_review for `income_text` - Review whether the data contract should encode this deterministic finding as an explicit validation rule.
