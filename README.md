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

Phase 2 adds a real deterministic audit core. The `dqa audit` command now loads
a CSV dataset, profiles it, infers basic column roles, runs deterministic checks,
calculates a readiness score, writes `reports/audit.json`, and prints a Rich
terminal summary.

## Installation

```bash
pip install -e ".[dev]"
```

## CLI

```bash
dqa --help
dqa version
dqa audit examples/datasets/classification_dirty.csv --target label
dqa audit examples/datasets/classification_dirty.csv --target label --output-dir reports
```

Planned commands remain available as placeholders:

```bash
dqa report reports/audit.json --format markdown
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contract.json
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
```

Exact counts can change as deterministic checks evolve.

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
- [Roadmap](docs/roadmap.md)
- [Safety](docs/safety.md)

## Roadmap

- Phase 1: Foundation
- Phase 2: Audit models and issue schema
- Phase 3: Deterministic checks and scoring expansion
- Phase 4: Reports
- Phase 5: Contracts and validation
- Phase 6: AI review engine and LangGraph workflow
- Phase 7: Public release polish

## Safety Principles

- The deterministic audit engine is the source of truth.
- AI cannot invent findings.
- AI cannot change scores.
- AI cannot modify datasets.
- AI review text must reference deterministic issue IDs once available.

## Development

```bash
pip install -e ".[dev]"
ruff check .
python -m pytest
```

## License

MIT License. See [LICENSE](LICENSE).
