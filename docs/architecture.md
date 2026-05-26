# Architecture

Dataset Quality Auditor is planned as a CLI-first developer tool for assessing
tabular machine learning dataset readiness before training.

## Deterministic Audit Engine

The deterministic audit engine is the source of truth. It will own dataset
profiling, issue detection, scoring, stable issue identifiers, and structured
audit output. Later AI components must consume this output rather than inventing
their own findings.

## Reports

Reports will transform deterministic audit output into formats suitable for
humans and automation. Planned formats include terminal summaries, JSON,
Markdown, and HTML.

## Contracts

Contracts will capture expected dataset properties such as target column,
schema, allowed values, nullability, and readiness constraints. Validation will
compare incoming datasets against these contracts deterministically.

## AI Review Layer

The AI review layer will explain, group, and prioritize deterministic findings.
It will not create findings, change scores, or modify datasets. AI responses
must reference deterministic issue IDs once the issue schema exists.

## Provider Abstraction

AI providers will be isolated behind a provider interface so OpenAI, Ollama, or
other backends can be added without coupling the audit engine to a vendor.

## LangGraph Workflow

LangGraph orchestration is planned for a later phase. It will coordinate review
steps around deterministic audit artifacts and provider abstractions, not replace
the audit engine.
