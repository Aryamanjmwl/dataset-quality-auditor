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

## Checks

Phase 2 includes checks for missing values, duplicate rows, constant columns,
high-cardinality categorical columns, class imbalance, ID-like columns, and
datatype risks.

## Audit JSON

The audit JSON contains:

- `audit_id`
- `created_at`
- `dataset_path`
- `target_column`
- `profile`
- `issues`
- `score`
- `metadata`

Metadata marks the result as deterministic and not AI-generated.
