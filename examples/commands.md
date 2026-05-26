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
