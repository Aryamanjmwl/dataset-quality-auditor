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
  |     |     +-- train/test checks
  |     +-- deterministic scoring
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
  +-- review command
        +-- provider abstraction
        +-- mock provider
        +-- graph-style workflow
        +-- guardrails
        +-- reports/ai_review.json
```

## CLI Layer

The CLI is implemented with Typer and uses Rich for terminal summaries. It is
the primary interface for audit, reports, contracts, validation, and AI review.

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
mismatch, exact train/test overlap, numeric drift, and categorical drift.

## Reports

Reports consume deterministic audit JSON. They produce JSON, Markdown, and
self-contained HTML artifacts without adding findings or changing scores.

## Contracts and Validation

Contracts are YAML files generated from deterministic profiles. Validation
checks required columns, logical types, nullable constraints, missingness,
numeric ranges, categorical values, and uniqueness hints.

## AI Review Foundation

AI review reads audit JSON rather than raw datasets by default. The current
provider is `mock`, which is deterministic and local.

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

Guardrails validate every AI review before writing output. Reviews are rejected
if they reference unknown issue IDs, change readiness scores, change score
bands, or fail to mark deterministic source metadata.

## Provider Abstraction

Providers implement a small review interface. Future OpenAI-compatible and
Ollama/local adapters can plug into the same boundary without changing the
deterministic audit engine.
