# Command Examples

## Install

```bash
pip install -e ".[dev]"
```

## Audit JSON

```bash
dqa audit examples/datasets/classification_dirty.csv --target label
```

## Audit All Formats

```bash
dqa audit examples/datasets/classification_dirty.csv --target label --format all
```

## Audit Train/Test Split

```bash
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
```

## Audit With Threshold Config

```bash
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --config examples/audit-config.yaml
```

## Summarize Audit JSON

```bash
dqa summary reports/audit.json --format json
```

## Run CI Gate

```bash
dqa gate reports/audit.json --min-score 80 --max-critical 0 --max-high 0
```

## Regenerate Markdown Report

```bash
dqa report reports/audit.json --format markdown
```

## Regenerate HTML Report

```bash
dqa report reports/audit.json --format html
```

## Generate Data Contract

```bash
dqa contract examples/datasets/classification_dirty.csv --target label
```

## Validate Dataset Against Contract

```bash
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
```

## Guarded Review With Mock Provider

```bash
dqa review reports/audit.json --provider mock
```

## Guarded Review Graph Workflow

```bash
dqa review reports/audit.json --provider mock --workflow graph
```

## Public Demo Sequence

```bash
pip install -e ".[dev]"
dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --config examples/audit-config.yaml
dqa summary reports/audit.json --format json
dqa gate reports/audit.json --min-score 80 --max-critical 0 --max-high 0
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
dqa review reports/audit.json --provider mock --workflow graph
```
