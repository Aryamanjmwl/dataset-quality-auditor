# Dataset Quality Auditor

Dataset Quality Auditor is a CLI-first Python package for auditing tabular
machine learning datasets before training.

The project is being built as a deterministic-first developer tool. The audit
engine will be the source of truth for findings, issue IDs, scores, and dataset
readiness signals. AI integrations are planned later to explain and prioritize
deterministic findings, not to invent findings or modify data.

## Mission

Help ML engineers and data teams catch dataset readiness problems before model
training, while keeping audit results reproducible, inspectable, and safe for
automation.

## What the Tool Does

Dataset Quality Auditor is intended to:

- Audit tabular datasets from the command line.
- Produce deterministic readiness findings and scores.
- Generate reports for humans and CI workflows.
- Create dataset contracts for repeatable validation.
- Add an AI review layer later for explanation and prioritization.

## Deterministic-First Principle

Deterministic audit logic is the authority. AI may later summarize, group, and
prioritize audit findings, but it must not:

- Invent findings.
- Change scores.
- Modify datasets.
- Discuss issues without referencing deterministic issue IDs.

## Current Status

This repository is in early Phase 1 foundation work. The package structure,
CLI skeleton, documentation, tests, and CI are in place. The full audit engine,
contracts, reports, provider integrations, and LangGraph workflow are planned
for later phases.

## Installation

```bash
pip install -e ".[dev]"
```

## CLI

```bash
dqa --help
dqa version
dqa audit examples/datasets/classification_dirty.csv --target label
dqa report audit.json --format markdown
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contract.json
```

The current `audit` command validates that the dataset path exists and prints a
clear planning message with the dataset path and target column. Other commands
are professional placeholders until their roadmap phases are implemented.

## Roadmap

- Phase 1: Foundation
- Phase 2: Audit models and issue schema
- Phase 3: Deterministic checks and scoring
- Phase 4: Reports
- Phase 5: Contracts and validation
- Phase 6: AI review engine and LangGraph workflow
- Phase 7: Public release polish

See [docs/roadmap.md](docs/roadmap.md) for more detail.

## Safety Principles

- The deterministic audit engine is the source of truth.
- AI cannot invent findings.
- AI cannot change scores.
- AI cannot modify datasets.
- AI review text must reference deterministic issue IDs once available.

See [docs/safety.md](docs/safety.md) for the full safety model.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the intended package
architecture, including the deterministic audit engine, reports, contracts, AI
review layer, provider abstraction, and future LangGraph workflow.

## License

MIT License. See [LICENSE](LICENSE).
