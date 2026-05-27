# Data Contracts

Data contracts capture deterministic expectations about a tabular ML dataset.
They help teams validate that future datasets still look compatible with the
dataset that was profiled before training.

Contracts in Dataset Quality Auditor are lightweight YAML files. They are
generated from observed dataset evidence and do not use AI.

## Why Contracts Matter

ML training and inference pipelines can fail quietly when columns disappear,
types drift, categories change, or numeric ranges move outside the data seen
during review. Contracts make those assumptions explicit and repeatable.

## Generate A Contract

```bash
dqa contract examples/datasets/classification_dirty.csv --target label
```

By default this writes:

```text
contracts/classification_dirty_contract.yaml
```

## Validate A Dataset

```bash
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
```

By default this writes:

```text
reports/validation_result.json
```

## What DQA Generates

The generated contract includes:

- Dataset source, target column, row count, and column count.
- All observed columns as required columns.
- Column roles from deterministic schema inference.
- Logical types such as numeric, categorical, datetime, text, or unknown.
- Observed pandas dtypes.
- Missingness and uniqueness percentages.
- Numeric min and max constraints for numeric columns.
- Allowed values for low-cardinality categorical columns.
- Human-review hints for ID-like columns.
- Target classes and class distribution when a target is provided.

## Validation Checks

Validation checks:

- Required columns exist.
- Logical type compatibility.
- Non-nullability when nullable is false.
- Missing percent does not exceed the contract limit.
- Numeric values stay within min/max constraints.
- Categorical values stay within allowed values.
- ID-like uniqueness hints remain high-uniqueness.

Validation does not stop at the first failure. It collects all deterministic
checks and writes a JSON result.

## Safety And Limitations

Contracts are inferred from observed data. They should be reviewed before being
used as production gates, especially for ID columns, sensitive columns, and
columns whose prediction-time availability may differ from training-time data.

DQA contracts do not modify datasets and do not make AI-generated claims.
