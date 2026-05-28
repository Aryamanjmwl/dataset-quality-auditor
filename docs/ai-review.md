# AI Review

Dataset Quality Auditor is designed to support AI-assisted review while keeping
the deterministic audit engine as the source of truth.

The current implementation includes a provider-agnostic review foundation, a
deterministic mock provider, and a local graph-style workflow. These paths do
not call external APIs or require API keys.

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

## Review Workflows

Two workflows are available:

- `provider`: directly asks the deterministic mock provider to create the
  guarded review JSON.
- `graph`: runs a local node-based workflow before final guardrail validation.

```bash
dqa review reports/audit.json --provider mock
dqa review reports/audit.json --provider mock --workflow graph
```

The graph workflow is intentionally small and CI-friendly. It mirrors a
LangGraph-style review pipeline without adding external model calls.

Graph nodes:

- Risk prioritizer: orders existing deterministic issues by severity.
- Fix recommender: converts existing issue recommendations into safe next steps.
- Contract advisor: suggests contract rules to review without mutating contracts.
- Report writer: writes a Markdown AI-assisted review.
- Output validator: validates the final review with guardrails before writing.

Graph output:

```text
reports/ai_review.json
reports/ai_review.md
```

## Provider-Agnostic Design

Providers implement a small interface that accepts deterministic audit output
and returns JSON-serializable review output. Future OpenAI and Ollama providers
can plug into this interface without changing the audit engine. Future real
providers may also be placed behind the graph nodes, but the deterministic audit
JSON remains the only source of findings and scores.

## Guardrails

Every review is validated before it is written:

- Every referenced issue ID must exist in `audit.json`.
- Readiness score must match `audit.json`.
- Score band must match `audit.json`.
- Metadata must mark the review as AI-generated and deterministically sourced.

Unsupported output is rejected with a clear error.
