# Dataset Quality Auditor

[![CI](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A deterministic-first, AI-assisted CLI for auditing machine learning datasets
before training — with readiness scoring, reproducible reports, validation
contracts, and guarded AI review.

## Why This Exists

ML projects often fail quietly before training starts: target leakage, unstable
schemas, high-cardinality identifiers, train/test overlap, drift, missingness,
and brittle data types can all make evaluation misleading. Dataset Quality
Auditor helps catch those risks early from the command line.

This project is not positioned as a replacement for Great Expectations,
Pandera, or Evidently. It is a lightweight ML-readiness auditor focused on
deterministic issue evidence, scoring, reports, contracts, and guarded AI
review.

## Key Features

- CLI-first workflow with Typer and Rich.
- Deterministic audit engine for tabular CSV datasets.
- Single-dataset and train/test audit modes.
- Checks for missingness, duplicates, constants, cardinality, imbalance,
  ID-like columns, datatype risks, outliers, correlation, leakage candidates,
  schema mismatch, overlap, and drift.
- Deterministic readiness score with structured issue evidence.
- JSON, Markdown, and self-contained HTML reports.
- YAML data contract generation and validation.
- Guarded mock AI review and local graph-style review workflow.
- pytest, ruff, and GitHub Actions CI.

## Quickstart

```bash
pip install -e ".[dev]"

dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
dqa review reports/audit.json --provider mock --workflow graph
```

Generated runtime outputs are written to `reports/` and `contracts/`. Curated
sample artifacts are committed under `examples/`.

## CLI Usage Examples

```bash
dqa version
dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
dqa report reports/audit.json --format html
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
dqa review reports/audit.json --provider mock
dqa review reports/audit.json --provider mock --workflow graph
```

## Example Outputs

Audit and report commands create:

- `reports/audit.json`
- `reports/audit_report.md`
- `reports/audit_report.html`

Contract and validation commands create:

- `contracts/classification_dirty_contract.yaml`
- `reports/validation_result.json`

AI review commands create:

- `reports/ai_review.json`
- `reports/ai_review.md` when `--workflow graph` is used

Curated examples are available in:

- `examples/reports/`
- `examples/contracts/`
- `examples/validation/`

## Architecture Overview

```text
Typer CLI
  -> deterministic audit engine
      -> profiler
      -> schema inference
      -> check registry
      -> readiness scoring
  -> reports
  -> contracts and validation
  -> guarded AI review
      -> provider workflow
      -> graph workflow
      -> guardrails
```

The deterministic audit engine is the source of truth. Reports, contracts, and
AI review consume audit output instead of inventing findings.

## Deterministic-First Safety Model

- AI does not invent findings.
- AI does not create issue IDs.
- AI does not change readiness scores or score bands.
- AI does not modify datasets.
- AI output must reference deterministic issue IDs.
- Unsupported AI review output is rejected by guardrails.

## AI Review Workflow

The current AI provider is a local deterministic mock provider. It requires no
API keys and makes no external calls.

```bash
dqa review reports/audit.json --provider mock
dqa review reports/audit.json --provider mock --workflow graph
```

The graph workflow runs local nodes for risk prioritization, safe fix
recommendations, contract advice, Markdown review writing, and output
validation. OpenAI-compatible and Ollama/local provider adapters are future
work.

## Data Contracts

```bash
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
```

Contracts are inferred from observed deterministic profiles. They are useful
starting points, not human-free governance. ID columns, sensitive fields, and
prediction-time availability should still be reviewed.

## Reports

```bash
dqa report reports/audit.json --format markdown
dqa report reports/audit.json --format html
dqa report reports/audit.json --format all
```

Reports only display deterministic audit findings and metadata. They do not
modify audit scores or add new issues.

## Roadmap

Completed MVP foundations:

- Package foundation and CI.
- Deterministic audit engine and advanced ML checks.
- Reports, contracts, validation, mock AI review, and graph workflow.
- Curated public demo datasets and sample artifacts.

Future work:

- OpenAI-compatible provider.
- Optional Ollama/local provider.
- Optional real LangGraph integration.
- More statistical drift tests.
- Demo GIF or video.
- v0.1.0 release.

## Contributing

Contributions are welcome. Please run the local quality gates before opening a
pull request:

```bash
ruff check .
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

MIT License. See [LICENSE](LICENSE).
