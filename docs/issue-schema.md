# Issue Schema

Audit issues are structured objects produced by deterministic checks.

## Fields

- `issue_id`: Stable identifier for the issue instance.
- `check_id`: Identifier for the deterministic check that produced the issue.
- `title`: Human-readable issue title.
- `severity`: One of `critical`, `warning`, or `info`.
- `risk_level`: One of `high`, `medium`, or `low`.
- `status`: Current issue status, usually `failed`.
- `scope`: Dataset, column, and inferred role affected by the issue.
- `evidence`: Metric, observed value, threshold, comparison, and details.
- `ml_impact`: Why the issue matters for model training or evaluation.
- `recommendation`: Deterministic remediation guidance.
- `requires_human_review`: Whether the issue needs user confirmation.
- `reproducibility`: Check version and parameters used to produce the issue.

## AI Safety

Later AI review must reference deterministic `issue_id` values. AI may explain
or prioritize issues, but it cannot invent findings, change severity or scores,
or modify datasets.
