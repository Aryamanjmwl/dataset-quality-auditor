<div align="center">

# Dataset Quality Auditor

**Deterministic ML dataset auditing — before training, not after.**

[![CI](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.2.0-informational)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

---

`dqa` is a CLI-first tool that audits local CSV datasets for machine learning readiness. It produces a deterministic readiness score, structured evidence for every issue, and reproducible reports — all before a single training run begins.

**It is not a replacement for Great Expectations, Pandera, or Evidently.** It is a focused, lightweight auditor that answers one question: *is this dataset safe to train on?*

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [What Gets Checked](#what-gets-checked)
- [Scoring Model](#scoring-model)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Command Reference](#command-reference)
- [Data Contracts](#data-contracts)
- [AI Review Layer](#ai-review-layer)
- [Threshold Configuration](#threshold-configuration)
- [Issue Schema](#issue-schema)
- [Synthetic Demo Dataset](#synthetic-demo-dataset)
- [Architecture](#architecture)
- [Project Layout](#project-layout)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why This Exists

ML projects fail quietly before training starts. Target leakage, schema drift, train/test overlap, high-cardinality identifiers, and brittle types can all produce misleading evaluation metrics — without a single error message.

`dqa` catches those risks deterministically, from the command line, with evidence you can trace back to the exact row or column that triggered the flag. Every issue has a stable ID, a measured threshold, and a recommendation. Nothing is invented.

---

## What Gets Checked

### Single-dataset checks

| Check | What it detects |
|---|---|
| **Missing values** | Columns exceeding configurable missing-rate thresholds |
| **Duplicate rows** | Exact duplicate rows that can bias training and validation |
| **Constant columns** | Zero-variance features (warning) and constant targets (critical) |
| **High cardinality** | Categorical columns unlikely to generalise |
| **ID-like columns** | Near-unique columns that are probably identifiers, not features |
| **Class imbalance** | Dominant target classes in classification targets |
| **Datatype risks** | Object-typed columns that mostly parse as numeric |
| **Outlier risk** | IQR-based outlier detection with configurable severity bands |
| **Correlation risk** | Near-collinear numeric feature pairs (|r| ≥ 0.95) |
| **Target leakage** | Name-signal + correlation gating; categorical target-mapping |

### Train / test checks *(requires `--test`)*

| Check | What it detects |
|---|---|
| **Schema mismatch** | Missing/extra columns, dtype mismatches, type-kind mismatches |
| **Train/test overlap** | Exact duplicate rows across splits — inflates eval metrics |
| **Numeric drift** | Mean-shift heuristic (`|Δμ| / σ_train`) |
| **KS-test drift** | Kolmogorov-Smirnov two-sample test per numeric column (`scipy` optional) |
| **Categorical drift** | Unseen categories, missing train categories, dominant-frequency shifts |
| **Target distribution drift** | Proportional shift in target class distributions |

---

## Scoring Model

Scores start at **100** and deductions are applied per issue, capped by severity tier to prevent many minor issues from outweighing a single critical one.

| Severity | Base deduction | Tier cap |
|---|---|---|
| `critical` | −20 | −40 max |
| `warning` | −8 | −32 max |
| `info` | −2 | −10 max |
| `requires_human_review` | −2 extra | uncapped |

> Scores are clamped to `[0, 100]`. Human-review deductions are applied on top of the capped severity total.

**Score bands**

| Band | Range | Meaning |
|---|---|---|
| `ready` | 85 – 100 | Proceed with awareness of any flagged issues |
| `needs_attention` | 60 – 84 | Review flagged issues before training |
| `high_risk` | 0 – 59 | Address critical issues before training |

The score is deterministic. AI cannot adjust, reinterpret, or override it.

---

## Installation

**Requirements:** Python 3.10 or later. `scipy` is optional (enables KS-drift tests).

```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"          # installs scipy for KS-drift tests
```

Verify the install:

```bash
dqa version
python -m pytest
```

---

## Quickstart

### Single-dataset audit

```bash
dqa audit examples/datasets/classification_dirty.csv \
  --target label \
  --format all
```

Writes `reports/audit.json`, `reports/audit_report.md`, `reports/audit_report.html`.

### Train / test audit

```bash
dqa audit examples/datasets/train_sample.csv \
  --test examples/datasets/test_sample.csv \
  --target label \
  --format all
```

Activates schema mismatch, overlap, drift, and KS-test checks.

### CI quality gate

```bash
# Run audit
dqa audit data/train.csv --test data/test.csv --target label

# Block the pipeline if quality is below threshold
dqa gate reports/audit.json --min-score 80 --max-critical 0
```

`dqa gate` exits with code `0` on pass, non-zero on fail — wires directly into GitHub Actions, GitLab CI, or any shell pipeline.

---

## Command Reference

### `dqa audit`

Run all deterministic checks and write `audit.json`.

```
dqa audit DATASET
  --target    TARGET          target column name
  --test      TEST_DATASET    optional test CSV (enables train/test checks)
  --config    CONFIG.yaml     optional threshold overrides
  --format    json|markdown|html|all   (default: json)
  --output-dir DIR            (default: reports/)
```

### `dqa report`

Regenerate report files from an existing `audit.json` without re-running checks.

```
dqa report AUDIT_JSON --format json|markdown|html|all
```

### `dqa summary`

Print a compact audit summary to the terminal.

```
dqa summary AUDIT_JSON --format text|json
```

### `dqa gate`

Evaluate CI gate rules against an existing `audit.json`.

```
dqa gate AUDIT_JSON
  --min-score       SCORE      minimum passing score (0–100)
  --max-critical    N          maximum allowed critical issues
  --max-high        N          maximum allowed high-risk issues
  --max-medium      N          maximum allowed medium-risk issues
  --max-human-review N         maximum issues requiring human review
```

### `dqa contract`

Generate a YAML data contract from an observed dataset.

```
dqa contract DATASET --target TARGET --output-dir contracts/
```

### `dqa validate`

Validate a dataset against a previously generated contract.

```
dqa validate DATASET --contract CONTRACT.yaml --output-dir reports/
```

### `dqa review`

Generate a guarded AI-assisted review from `audit.json`.

```
dqa review AUDIT_JSON
  --provider   mock|anthropic
  --workflow   provider|graph
  --output-dir DIR
```

### `dqa version`

```bash
dqa version
```

---

## Output Files

| Command | File | Description |
|---|---|---|
| `audit` | `reports/audit.json` | Canonical audit record — source of truth for all downstream commands |
| `audit --format markdown` | `reports/audit_report.md` | Human-readable Markdown report |
| `audit --format html` | `reports/audit_report.html` | Self-contained HTML report |
| `summary` | terminal | Compact text or JSON summary |
| `gate` | terminal + exit code | Pass/fail gate result |
| `contract` | `contracts/<name>_contract.yaml` | Generated YAML data contract |
| `validate` | `reports/validation_result.json` | Contract validation result |
| `review` | `reports/ai_review.json` | Guarded AI review |
| `review --workflow graph` | `reports/ai_review.md` | Markdown AI review narrative |

> `reports/` and `contracts/` are runtime outputs and are `.gitignore`d.
> Curated examples live under `examples/`.

---

## Data Contracts

Contracts capture deterministic expectations about a dataset so you can validate future data against them.

```bash
# Generate a contract from your training data
dqa contract examples/datasets/classification_dirty.csv --target label

# Validate a new dataset against the contract
dqa validate new_data.csv --contract contracts/classification_dirty_contract.yaml
```

A generated contract records: required columns, logical types, nullability, numeric min/max constraints, allowed categorical values, target class distribution, and uniqueness hints for ID-like columns.

**Contracts are a starting point, not a production gate without review.** ID columns, sensitive fields, and columns whose availability differs between training and inference should be inspected manually before the contract is used as a hard validator.

---

## AI Review Layer

The AI review layer is optional and additive. It reads `audit.json` and produces a structured commentary — it cannot change the audit's findings.

```bash
# Mock review (no API key, no external calls)
dqa review reports/audit.json --provider mock

# Graph workflow (5-node pipeline: prioritise → fix → contract → write → validate)
dqa review reports/audit.json --provider mock --workflow graph

# Anthropic provider (requires ANTHROPIC_API_KEY)
dqa review reports/audit.json --provider anthropic
```

### Safety guarantees (enforced by guardrails at runtime)

The guardrails module validates every AI review before it is written to disk. Any review that violates the following rules is **rejected with an error**:

- AI may not invent findings or create issue IDs not present in `audit.json`
- AI may not change the readiness score or score band
- AI may not modify datasets
- Every referenced issue must trace back to a deterministic issue ID
- Review metadata must declare `ai_generated: true` and `deterministic_source: true`

The deterministic audit engine is always the source of truth.

---

## Threshold Configuration

All drift and quality thresholds can be overridden with a YAML config file:

```yaml
# examples/audit-config.yaml
thresholds:
  numeric_drift:
    mean_shift_std_ratio: 1.0      # flag when |Δμ| / σ_train ≥ this
  categorical_drift:
    dominant_category_shift: 0.30  # flag dominant-frequency shifts ≥ this
    missing_category_ratio: 0.50   # flag when ≥ this share of train categories absent in test
  target_distribution_drift:
    warning_shift: 0.25            # warning when max class proportion shifts ≥ this
    critical_shift: 0.50           # critical when max class proportion shifts ≥ this
```

```bash
dqa audit train.csv --test test.csv --target label --config examples/audit-config.yaml
```

These are readiness thresholds, not statistical significance tests.

---

## Issue Schema

Every issue produced by the audit engine is a structured, immutable object:

| Field | Type | Description |
|---|---|---|
| `issue_id` | `str` | Stable, reproducible identifier for this issue instance |
| `check_id` | `str` | The check that produced this issue |
| `title` | `str` | Human-readable issue title |
| `severity` | `critical \| warning \| info` | Drives score deductions |
| `risk_level` | `high \| medium \| low` | Display/filtering metadata; does not affect score |
| `status` | `str` | Always `"failed"` for flagged issues |
| `scope` | `dict` | Dataset, column, and inferred role |
| `evidence` | `dict` | Metric, observed value, threshold, comparison, details |
| `ml_impact` | `str` | Why this issue matters for training or evaluation |
| `recommendation` | `str` | Deterministic remediation guidance |
| `requires_human_review` | `bool` | Whether the issue needs manual confirmation |
| `reproducibility` | `dict` | Check version and parameters used |

---

## Synthetic Demo Dataset

A 2,000-row synthetic training set and 500-row test set are included under `examples/datasets/` with deliberately planted issues: target leakage, class imbalance, numeric drift, categorical drift, and missing values.

```bash
# Audit the synthetic training set
dqa audit examples/datasets/synthetic_train.csv --target target --format all

# Audit with train/test comparison
dqa audit examples/datasets/synthetic_train.csv \
  --test examples/datasets/synthetic_test.csv \
  --target target --format all

# Run the CI gate (expected to fail — planted critical issues)
dqa gate reports/audit.json --min-score 60 --max-critical 0
```

The gate fails by design — `post_event_score` has a 0.97+ correlation with the target and will produce a critical leakage issue. That is the expected and correct outcome.

To regenerate the synthetic datasets:

```bash
python examples/datasets/generate_synthetic.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Entry points                                           │
│  CLI (dqa)  ·  Python API  ·  YAML config  ·  CI gate  │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  Deterministic audit engine  (engine.py)                │
│                                                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │  Profiler   │  │ Schema inference │  │  Context  │  │
│  │ dtype·stats │  │ role·id·datetime │  │ thresholds│  │
│  └─────────────┘  └──────────────────┘  └───────────┘  │
│                                                         │
│  10 single-dataset checks  ·  3 train/test checks       │
│  missing · duplicates · constants · cardinality         │
│  imbalance · id-like · datatypes · outliers             │
│  correlation · leakage · schema · overlap · drift       │
│                                                         │
│  Issue model  ·  Evidence  ·  Scoring (capped)         │
└──────┬────────────────┬───────────────────┬─────────────┘
       │                │                   │
┌──────▼──────┐ ┌───────▼────────┐ ┌───────▼──────────┐
│   Reports   │ │   Contracts    │ │   audit.json     │
│ JSON·MD·HTML│ │ generate·valid.│ │  source of truth │
└─────────────┘ └────────────────┘ └───────┬──────────┘
                                           │
                               ┌───────────▼───────────────┐
                               │  AI Review  (optional)    │
                               │  review_engine.py         │
                               │  ┌─────────┐ ┌─────────┐  │
                               │  │  Mock   │ │Anthropic│  │
                               │  │provider │ │provider │  │
                               │  └────┬────┘ └────┬────┘  │
                               │       └─────┬──────┘       │
                               │      ┌──────▼──────┐       │
                               │      │  Guardrails │       │
                               │      │ issue IDs   │       │
                               │      │ score locked│       │
                               │      └─────────────┘       │
                               └────────────────────────────┘
```

The deterministic audit engine is the source of truth. Reports, contracts, summaries, CI gates, and AI review all read from `audit.json` — they never add findings or change scores.

---

## Project Layout

```
dataset_quality_auditor/
├── audit/
│   ├── engine.py            # run_audit() — main orchestrator
│   ├── profiler.py          # column statistics and role inference
│   ├── schema.py            # id/datetime/feature role detection
│   ├── context.py           # AuditContext + DEFAULT_CONFIG thresholds
│   ├── scoring.py           # calculate_readiness_score() with severity caps
│   ├── severity.py          # CRITICAL / WARNING / INFO constants
│   ├── issues.py            # Issue dataclass (frozen, reproducible)
│   ├── evidence.py          # Evidence dataclass
│   ├── registry.py          # get_default_checks() / get_train_test_checks()
│   ├── config.py            # YAML threshold loader
│   ├── summary.py           # compact audit summaries and gate evaluation
│   └── checks/
│       ├── missing.py       cardinality.py   constants.py
│       ├── duplicates.py    datatypes.py     outliers.py
│       ├── imbalance.py     correlation.py   id_like.py
│       ├── leakage.py       drift.py         ks_drift.py
│       ├── schema_mismatch.py               overlap.py
│       └── __init__.py      # issue_id() + reproducibility() helpers
├── reports/
│   ├── json_report.py       markdown_report.py   html_report.py
│   └── templates/report.html.j2
├── contracts/
│   ├── generator.py         validator.py         schema.py
├── ai/
│   ├── guardrails.py        review_engine.py     prompts.py   schemas.py
│   └── providers/
│       ├── base.py          # AIReviewProvider Protocol
│       ├── mock.py          # deterministic mock (no API key)
│       └── anthropic_provider.py  # Claude adapter (ANTHROPIC_API_KEY)
├── agent/
│   ├── graph.py             state.py
│   └── nodes/
│       ├── risk_prioritizer.py     fix_recommender.py
│       ├── contract_advisor.py     report_writer.py
│       └── output_validator.py
├── utils/
│   ├── io.py                logging.py
└── cli.py                   # Typer CLI entry point
tests/                       # 116 tests, pytest + ruff
examples/
├── datasets/                # classification_dirty.csv · train/test samples · synthetic data
├── reports/                 # curated sample audit.json · HTML · ai_review
├── contracts/               # sample YAML contract
└── audit-config.yaml        # example threshold config
docs/                        # architecture · checks · scoring · contracts · AI review · safety
```

---

## Contributing

Contributions are welcome. Please run the local quality gates before opening a pull request:

```bash
ruff check .
python -m pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch conventions, commit style, and the PR template. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

To report a security issue, see [SECURITY.md](SECURITY.md).

---

## Roadmap

**Completed in v0.2.0**
- Per-severity scoring caps and `severity_totals` key
- KS-test drift detection (`scipy` optional extra)
- Tightened leakage name-signal detection (name + correlation required)
- Anthropic provider adapter with guardrail integration
- Synthetic demo datasets with planted issues
- Configurable audit thresholds and CI gate command

**Up next**
- Additional statistical drift tests with clear assumptions
- Richer report customisation options
- More contract validation rules
- Expanded documentation for ML pipeline integration

**Non-goals**
- Automatic dataset cleaning or mutation
- Unguarded AI-generated findings
- Replacing Great Expectations, Pandera, or Evidently
- Docker or cloud connectors in this release

---

## License

[MIT](LICENSE) — Dataset Quality Auditor contributors.
