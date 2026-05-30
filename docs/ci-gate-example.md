# CI Gate Example

`dqa gate` evaluates an existing `audit.json` and exits non-zero when the
configured gate fails. This makes it useful in CI after a deterministic audit
has already been generated.

Example GitHub Actions job:

```yaml
name: Dataset Quality Gate

on:
  pull_request:
  push:
    branches: [main]

jobs:
  dataset-quality-gate:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install package
        run: python -m pip install -e ".[dev]"

      - name: Run deterministic audit
        run: >
          dqa audit examples/datasets/train_sample.csv
          --test examples/datasets/test_sample.csv
          --target label
          --output-dir reports

      - name: Enforce audit gate
        run: >
          dqa gate reports/audit.json
          --min-score 80
          --max-critical 0
          --max-high 0
```

Tune `--min-score` and issue-count limits for your own datasets and risk
tolerance. Gate thresholds are deterministic readiness checks, not statistical
significance tests.
