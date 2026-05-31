# Roadmap

## Completed

- Professional Python package foundation.
- Typer CLI with Rich output.
- pytest, ruff, and GitHub Actions CI.
- Deterministic audit engine.
- Structured issue, evidence, profiling, and scoring models.
- JSON, Markdown, and HTML reports.
- YAML data contracts.
- Contract validation mode.
- Advanced ML-readiness checks.
- Train/test audit mode.
- Deterministic train/test drift checks.
- Configurable audit thresholds.
- Compact audit summaries and CI gates.
- Guarded mock/local review.
- Graph-style guarded review workflow.
- Curated public example datasets and sample artifacts.

## Next

- Curate additional sample outputs for common dataset risk scenarios.
- Prepare the next source release.
- Evaluate optional external provider adapters behind the existing guardrails.
- Evaluate optional real LangGraph integration.
- Add more statistical drift tests where evidence and assumptions are clear.
- Create a short demo GIF or video.

## Later

- Richer report customization.
- More contract validation rules.
- Additional tabular file formats.
- Expanded documentation for integration into ML training pipelines.

## Non-Goals For The MVP

- Automatic dataset cleaning or mutation.
- Unguarded generated findings.
- Replacing Great Expectations, Pandera, or Evidently.
- Streamlit or dashboard-first workflows.
- Docker, cloud connectors, or external LLM providers in the current release.
