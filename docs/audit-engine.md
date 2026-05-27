# Audit Engine

Dataset Quality Auditor uses a deterministic-first audit pipeline. The engine is
the source of truth for findings, evidence, and readiness scoring.

## Pipeline

1. Load a CSV dataset with pandas.
2. Validate that the requested target column exists.
3. Create an audit context with stable thresholds and package metadata.
4. Profile rows, columns, duplicates, missingness, cardinality, and basic types.
5. Infer cautious column roles such as `target`, `feature`, `id_candidate`, and
   `datetime_candidate`.
6. Run deterministic checks from the default registry.
7. Emit structured issue objects with evidence and reproducibility metadata.
8. Calculate a deterministic readiness score.
9. Write `audit.json` to the selected output directory.

## Audit Modes

### Single-Dataset Mode

`dqa audit data.csv --target label` profiles one dataset and runs deterministic
single-dataset checks. The audit JSON has:

```json
{
  "mode": "single_dataset",
  "profile": { "...": "single dataset profile" }
}
```

### Train/Test Mode

`dqa audit train.csv --test test.csv --target label` profiles train and test
datasets separately. It runs all single-dataset checks on the train dataset and
then runs train/test checks for schema mismatch, overlap, and drift.

The audit JSON has:

```json
{
  "mode": "train_test",
  "profile": {
    "train": { "...": "train profile" },
    "test": { "...": "test profile" }
  }
}
```

## Checks

Checks include missing values, duplicate rows, constant columns,
high-cardinality categorical columns, class imbalance, ID-like columns, datatype
risks, outlier risk, correlation risk, target leakage candidates, and optional
train/test checks for schema mismatch, overlap, and drift.

## Audit JSON

The audit JSON contains:

- `audit_id`
- `created_at`
- `dataset_path`
- `test_dataset_path`
- `mode`
- `target_column`
- `profile`
- `issues`
- `score`
- `metadata`

Metadata marks the result as deterministic and not AI-generated.
