# Reports

Dataset Quality Auditor reports convert deterministic audit JSON into formats
for developers, pull requests, and browser review.

Reports do not run new checks and do not invent findings. The deterministic
`audit.json` file remains the source of truth.

## Formats

- JSON: a pretty-printed copy of the deterministic audit result.
- Markdown: GitHub-ready summary with score, issues, columns, and next steps.
- HTML: self-contained visual report rendered with Jinja2 and simple CSS.

## Commands

```bash
dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa report reports/audit.json --format html
dqa report reports/audit.json --format markdown
dqa report reports/audit.json --format all
```

## Report Contents

Reports include:

- Executive summary
- Dataset overview
- Readiness score and deterministic deductions
- Issue summary grouped by severity
- Column overview
- Deduplicated recommendations from existing issues
- Reproducibility metadata

## Safety

Reports only display deterministic findings already present in audit JSON.
AI-generated report sections may be added later, but they will be clearly marked
and must reference deterministic issue IDs.
