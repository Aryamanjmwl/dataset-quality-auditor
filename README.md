# Dataset Quality Auditor

Dataset Quality Auditor is a CLI-first Python package for auditing tabular
machine learning datasets before training.

The project is deterministic-first: the audit engine is the source of truth for
findings, evidence, issue IDs, and readiness scoring. AI review is planned for a
later phase, but AI will only explain and prioritize deterministic findings. It
must not invent findings, change scores, or modify datasets.

## Current Status

Phase 3 adds a professional reporting layer. `dqa audit` runs the deterministic
core, writes `reports/audit.json`, and can also generate Markdown and HTML
reports. `dqa report` regenerates reports from an existing deterministic
`audit.json`.

## Installation

```bash
pip install -e ".[dev]"
```

## Audit

```bash
dqa audit examples/datasets/classification_dirty.csv --target label
dqa audit examples/datasets/classification_dirty.csv --target label --format all
```

Sample terminal output:

```text
Dataset Quality Auditor

Dataset: examples/datasets/classification_dirty.csv
Target: label
Rows: 10
Columns: 7

Readiness Score: 28/100
Band: high_risk

Issues:
Critical: 1
Warnings: 6
Info: 1

Audit JSON written to: reports/audit.json
Generated: reports/audit_report.md
Generated: reports/audit_report.html
```

## Reports

Reports only present findings from deterministic audit JSON.

```bash
dqa report reports/audit.json --format markdown
dqa report reports/audit.json --format html
dqa report reports/audit.json --format all
```

Output files:

- `reports/audit.json`
- `reports/audit_report.json`
- `reports/audit_report.md`
- `reports/audit_report.html`

See [docs/reports.md](docs/reports.md).

## Deterministic Checks

The audit engine currently checks missing values, duplicate rows, constant
columns, high cardinality, class imbalance, ID-like columns, and datatype risks.

## Documentation

- [Architecture](docs/architecture.md)
- [Reports](docs/reports.md)
- [Roadmap](docs/roadmap.md)
- [Safety](docs/safety.md)

## Development

```bash
pip install -e ".[dev]"
ruff check .
python -m pytest
```

## License

MIT License. See [LICENSE](LICENSE).
