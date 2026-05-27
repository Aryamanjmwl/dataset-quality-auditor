# AI Review

Dataset Quality Auditor is designed to support AI-assisted review while keeping
the deterministic audit engine as the source of truth.

Phase 6A adds the provider-agnostic review foundation and a deterministic mock
provider. It does not call external APIs and does not require API keys.

## Deterministic Boundary

AI review reads `audit.json`. It does not read or modify raw datasets by default.
This keeps review output traceable to deterministic issue IDs, scores, and
evidence already produced by the audit engine.

The review layer must not:

- Invent findings.
- Create new issue IDs.
- Change readiness scores.
- Change score bands.
- Modify datasets.
- Make unsupported claims beyond deterministic audit evidence.

## Mock Provider

The current supported provider is `mock`.

```bash
dqa review reports/audit.json --provider mock
```

The mock provider is deterministic. It prioritizes existing issues by severity,
copies the readiness score and score band from the audit JSON, creates safe next
steps from existing issue recommendations, and creates human-review questions
only for issues already marked `requires_human_review`.

Output:

```text
reports/ai_review.json
```

## Provider-Agnostic Design

Providers implement a small interface that accepts deterministic audit output
and returns JSON-serializable review output. Future OpenAI and Ollama providers
can plug into this interface without changing the audit engine.

## Guardrails

Every review is validated before it is written:

- Every referenced issue ID must exist in `audit.json`.
- Readiness score must match `audit.json`.
- Score band must match `audit.json`.
- Metadata must mark the review as AI-generated and deterministically sourced.

Unsupported output is rejected with a clear error.
