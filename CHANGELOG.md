# Changelog

All notable changes to Dataset Quality Auditor will be documented here.

## [0.2.0] - 2026-05-31

### Added

- Deterministic train/test drift checks.
- Configurable audit thresholds via `dqa audit --config`.
- Example audit config at `examples/audit-config.yaml`.
- Compact audit summaries with `dqa summary`.
- Deterministic CI/CD gates with `dqa gate`.
- CI gate usage documentation.
- CLI help text polish for local CSV workflows.
- Output artifact regression tests.

### Compatibility Notes

- Train/test audits may emit additional deterministic drift findings.
- Readiness scores may decrease when new drift findings are detected.
- Default thresholds preserve existing behaviour unless a config file is supplied.

## [0.1.0] - 2026-05-28

### Added

- Deterministic dataset audit engine
- Readiness scoring
- Structured audit issue schema
- Advanced ML-readiness checks
- Train/test audit mode
- JSON, Markdown, and HTML reports
- YAML data contract generation
- Contract validation mode
- Guarded mock AI review
- Graph-style AI review workflow
- Public example datasets and curated sample outputs
- GitHub Actions CI
- Documentation for quickstart, CLI usage, architecture, reports, contracts, AI review, and safety

### Notes

- AI review is currently mock/provider-agnostic only.
- Real OpenAI/Ollama providers are future work.
- The deterministic audit engine remains the source of truth.
