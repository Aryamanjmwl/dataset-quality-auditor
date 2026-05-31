# Architecture

Dataset Quality Auditor is a deterministic-first CLI package for ML dataset
readiness auditing.

## System Diagram

```text
User
  |
  v
Typer CLI + Rich output
  |
  +-- audit command
  |     |
  |     +-- CSV loader
  |     +-- profiler
  |     +-- schema inference
  |     +-- check registry
  |     |     +-- single-dataset checks
  |     |     +-- train/test drift checks
  |     +-- configurable thresholds
  |     +-- readiness scoring
  |     +-- reports/audit.json
  |
  +-- report command
  |     +-- JSON report
  |     +-- Markdown report
  |     +-- HTML report
  |
  +-- contract command
  |     +-- YAML contract generator
  |
  +-- validate command
  |     +-- contract validator
  |
  +-- summary command
  |     +-- compact audit JSON summary
  |
  +-- gate command
  |     +-- deterministic CI gate
  |
  +-- review command
        +-- provider-ready boundary
        +-- mock/local review
        +-- graph-style workflow
        +-- guardrails
        +-- reports/ai_review.json
```

## CLI Layer

The CLI is implemented with Typer and uses Rich for terminal summaries. It is
the primary interface for audit, reports, contracts, validation, summaries, CI
gates, and guarded mock/local review.

## Deterministic Audit Engine

The audit engine loads CSV files, profiles the dataset, infers cautious column
roles, runs checks, creates structured issues, calculates the readiness score,
and writes `audit.json`.

The deterministic engine is the source of truth for:

- Issue IDs.
- Issue severity.
- Evidence.
- Recommendations.
- Readiness score.
- Score band.

## Check Registry

Checks are registered centrally and return structured `Issue` objects. The
registry separates single-dataset checks from train/test checks so advanced
checks only run when a test dataset is provided.

## Single-Dataset Mode

Single-dataset mode audits one CSV file for risks such as missingness,
duplicates, constant columns, high cardinality, imbalance, ID-like columns,
datatype risks, outliers, correlation, and target leakage candidates.

## Train/Test Mode

Train/test mode audits a training CSV and a test CSV together. It detects schema
mismatch, exact train/test overlap, numeric drift, categorical drift, and target
distribution drift.

## Configurable Thresholds

Supported audit thresholds can be overridden with `dqa audit --config`. Missing
values fall back to deterministic defaults.

## Reports

Reports consume deterministic audit JSON. They produce JSON, Markdown, and
self-contained HTML artifacts without adding findings or changing scores.

## Contracts and Validation

Contracts are YAML files generated from deterministic profiles. Validation
checks required columns, logical types, nullable constraints, missingness,
numeric ranges, categorical values, and uniqueness hints.

## Summary And CI Gate

`dqa summary` and `dqa gate` consume existing audit JSON. They do not rerun
audits, modify datasets, or change readiness scores.

## Guarded Review Boundary

Guarded review reads audit JSON rather than raw datasets by default. The current
implementation is mock/local and deterministic.

## Graph-Style Review Workflow

The graph workflow is an internal sequential runner with LangGraph-compatible
node structure:

1. Risk prioritizer.
2. Fix recommender.
3. Contract advisor.
4. Report writer.
5. Output validator.

It writes guarded JSON and Markdown review artifacts.

## Guardrails

Guardrails validate every guarded review before writing output. Reviews are
rejected if they reference unknown issue IDs, change readiness scores, change
score bands, or fail to mark deterministic source metadata.

## Provider Abstraction

The review boundary keeps future provider adapters separate from deterministic
audit logic. No external LLM provider is included in the current release.

The deterministic audit engine is the source of truth. Reports, contracts,
summaries, CI gates, and guarded review consume audit output instead of
inventing findings.
