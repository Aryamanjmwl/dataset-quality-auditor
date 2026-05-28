# Quickstart

This guide runs the public MVP workflow with files committed in the repository.

## Install

```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor
pip install -e ".[dev]"
```

## Run a Single-Dataset Audit

```bash
dqa audit examples/datasets/classification_dirty.csv --target label --format all
```

Outputs:

- `reports/audit.json`
- `reports/audit_report.md`
- `reports/audit_report.html`

## Run a Train/Test Audit

```bash
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
```

This demonstrates train/test overlap, categorical drift, schema mismatch, and
numeric drift checks.

## Regenerate Reports

```bash
dqa report reports/audit.json --format html
dqa report reports/audit.json --format all
```

Reports are generated only from deterministic audit JSON.

## Generate a Contract

```bash
dqa contract examples/datasets/classification_dirty.csv --target label
```

Output:

- `contracts/classification_dirty_contract.yaml`

## Validate a Dataset

```bash
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
```

Output:

- `reports/validation_result.json`

## Run Mock AI Review

```bash
dqa review reports/audit.json --provider mock
dqa review reports/audit.json --provider mock --workflow graph
```

Outputs:

- `reports/ai_review.json`
- `reports/ai_review.md` for the graph workflow

Root `reports/` and `contracts/` directories are runtime outputs and are ignored
by Git. Curated public examples live under `examples/`.
