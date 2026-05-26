# Contributing

Thanks for helping improve Dataset Quality Auditor.

This project is currently in an early foundation phase. Contributions should keep
the deterministic audit engine as the source of truth and avoid introducing AI
behavior that can create findings, alter scores, or mutate datasets.

## Local Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Guidelines

- Keep changes focused and covered by tests.
- Prefer deterministic behavior for audit logic.
- Document public CLI or contract changes.
- Do not add AI providers, workflow orchestration, or dataset mutation features
  before the relevant roadmap phase.
