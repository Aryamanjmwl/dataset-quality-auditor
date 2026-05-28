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

## AI Review With Mock Provider

```bash
dqa review reports/audit.json --provider mock
```

## AI Review Graph Workflow

```bash
dqa review reports/audit.json --provider mock --workflow graph
```
