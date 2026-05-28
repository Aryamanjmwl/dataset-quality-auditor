# Dataset Quality Auditor v0.1.0

## Summary

Dataset Quality Auditor v0.1.0 is the first public MVP release of a
deterministic-first, AI-assisted CLI for auditing tabular machine learning
datasets before training.

The deterministic audit engine is the source of truth for findings, evidence,
issue IDs, severity, recommendations, and readiness scoring. AI review is local,
mock-only, and guarded in this release.

## Highlights

- Deterministic audit engine for CSV datasets.
- Single-dataset and train/test audit modes.
- Advanced ML-readiness checks for missingness, duplicates, constants,
  cardinality, imbalance, ID-like columns, datatype risks, outliers,
  correlation, leakage candidates, schema mismatch, overlap, and drift.
- Readiness score with structured issue evidence.
- JSON, Markdown, and self-contained HTML reports.
- YAML data contract generation.
- Contract validation mode.
- Guarded mock AI review.
- Graph-style review workflow with local deterministic nodes.
- Public example datasets and curated sample artifacts.
- pytest, ruff, and GitHub Actions CI.

## CLI Commands

```bash
pip install -e ".[dev]"

dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
dqa report reports/audit.json --format html
dqa contract examples/datasets/classification_dirty.csv --target label
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
dqa review reports/audit.json --provider mock --workflow graph
```

## Safety Model

- The deterministic audit engine remains the source of truth.
- AI review cannot invent findings.
- AI review cannot create new issue IDs.
- AI review cannot change readiness scores or score bands.
- AI review cannot modify datasets.
- AI review output must reference deterministic issue IDs.
- Unsupported AI review output is rejected by guardrails.

## Known Limitations

- Mock AI provider only.
- No automatic data cleaning.
- Inferred contracts need human review.
- Leakage findings are candidates, not definitive proof.
- Not a replacement for full validation platforms.

## Next Steps

- Add an OpenAI-compatible provider behind the existing guardrails.
- Add an optional Ollama/local provider.
- Evaluate optional real LangGraph integration.
- Expand statistical drift checks.
- Publish a short demo GIF or video.
