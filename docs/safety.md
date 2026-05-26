# Safety Principles

Dataset Quality Auditor is deterministic-first.

## AI Cannot Invent Findings

AI may explain or prioritize findings later, but every issue it discusses must
come from deterministic audit output.

## AI Cannot Change Scores

Scores are produced by deterministic logic. AI may describe why a score matters,
but it cannot adjust, reinterpret, or override the numeric result.

## AI Cannot Modify Datasets

The tool may later suggest remediation steps, but AI components must not directly
edit, clean, impute, delete, or rewrite dataset files.

## AI Must Reference Deterministic Issue IDs

Once issue IDs are implemented, AI-generated review text must cite those IDs so
users can trace every statement back to the audit engine.
