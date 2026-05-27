# Dataset Quality Auditor

Dataset Quality Auditor is a CLI-first Python package for auditing tabular
machine learning datasets before training.

The project is deterministic-first: the audit engine is the source of truth for
findings, evidence, issue IDs, and readiness scoring. AI review is planned for a
later phase, but AI will only explain and prioritize deterministic findings. It
must not invent findings, change scores, or modify datasets.

## Mission

Help ML engineers and data teams catch dataset readiness problems before model
training while keeping audit results reproducible, inspectable, and safe for
automation.

## Current Status

The repository includes the official Phase 2 deterministic audit core and the
Phase 3 reporting layer. The `dqa audit` command loads a CSV dataset, profiles
it, infers basic column roles, runs deterministic checks, calculates a readiness
score, writes `reports/audit.json`, and prints a Rich terminal summary.

Reports can be generated during audit or regenerated later from the deterministic
audit JSON.

## Installation

```bash
pip install -e ".[dev]"
```

## Audit

```bash
dqa audit examples/datasets/classification_dirty.csv --target label
dqa audit examples/datasets/classification_dirty.csv --target label --output-dir reports
dqa audit examples/datasets/classification_dirty.csv --target label --format all
```

## Example Output

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

Exact counts can change as deterministic checks evolve.

## Reports

Reports only present findings from deterministic audit JSON. They do not invent
findings, change scores, or modify datasets.

```bash
dqa report reports/audit.json --format json
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

Phase 2 includes checks for:

- Missing values
- Duplicate rows
- Constant columns
- High-cardinality categorical columns
- Class imbalance
- Suspicious ID-like columns
- Datatype risks such as numeric values stored as object strings

## Documentation

- [Architecture](docs/architecture.md)
- [Audit engine](docs/audit-engine.md)
- [Issue schema](docs/issue-schema.md)
- [Scoring](docs/scoring.md)
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
