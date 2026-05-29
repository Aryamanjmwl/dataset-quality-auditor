# Deterministic Checks

Dataset Quality Auditor checks are deterministic and evidence-backed. They emit
structured issues only when observed data crosses explicit rules.

## Single-Dataset Checks

### Missing Values

Detects columns whose missing percent exceeds configured thresholds. Evidence
includes missing count, total rows, and missing percent.

### Duplicate Rows

Detects duplicate rows in the audited dataset. Duplicate-heavy datasets can bias
training and validation.

### Constant Columns

Flags constant feature columns as warning issues and constant targets as
critical issues.

### Cardinality And ID-Like Columns

Flags high-cardinality categorical columns and ID-like candidates. ID-like
signals require human review because the tool cannot know prediction-time
availability.

### Class Imbalance

Detects dominant target classes for classification-like targets. Evidence
includes class distribution and dominant class ratio.

### Datatype Risks

Detects object columns that mostly parse as numeric. This can indicate a schema
or ingestion inconsistency.

### Outlier Risk

Uses the IQR rule for numeric features. Outlier percent at or above 5 percent is
a warning; at or above 15 percent is critical. Evidence includes bounds,
outlier count, and outlier percent. The recommendation is to inspect outliers
and use robust preprocessing where appropriate, not blindly remove rows.

### Correlation Risk

Computes absolute Pearson correlation between numeric feature pairs, excluding
the target. Correlations at or above 0.95 produce warning issues. Evidence
includes both columns and the correlation value.

### Target Leakage Candidates

Uses candidate language only. Signals include target-like feature names, very
high numeric correlation with the target, and near one-to-one categorical
mapping with the target. These issues require human review.

## Train/Test Checks

### Schema Mismatch

Detects missing test feature columns, extra test columns, dtype mismatches, and
inferred type-kind mismatches. Missing test feature columns are critical, extra
test columns are info, and dtype/type-kind mismatches are warnings. Evidence
includes train columns, test columns, missing columns, extra columns, dtype
mismatches, and type-kind mismatches.

### Train/Test Overlap

Detects exact duplicate rows across train and test. Any overlap is critical
because it can inflate evaluation metrics. Evidence includes overlap count, test
row count, and overlap percent of test.

### Numeric Drift

Compares numeric feature means between train and test using a deterministic mean
shift rule: `abs(test_mean - train_mean) / train_std`. A shift at or above 0.5 is
info; at or above 1.0 is warning. This is not a statistical significance claim.

### Categorical Drift

Compares observed category sets and dominant category frequencies. Unseen test
categories are warnings. Large missing category shifts are info for now.
Strong dominant-category changes are warnings. Evidence includes capped examples
of unseen/missing categories, unique counts, top categories, top frequencies,
and the deterministic shift value.

### Target Distribution Drift

When the target column exists in both train and test, compares normalized target
value distributions. A maximum class proportion shift at or above 0.25 is a
warning; at or above 0.50 is critical. This is a deterministic readiness signal,
not a statistical significance test.

## Limitations

These checks are readiness signals, not proof of model failure. They do not
modify data and do not use AI. Future AI review may explain these deterministic
issues, but it must reference issue IDs and cannot invent findings.
