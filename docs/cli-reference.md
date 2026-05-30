# CLI Reference

Dataset Quality Auditor exposes the `dqa` command after installation.

## `dqa version`

Purpose: show the installed package version.

Syntax:

```bash
dqa version
```

Output: terminal version text.

## `dqa audit`

Purpose: run deterministic dataset readiness checks and write `audit.json`.

Syntax:

```bash
dqa audit DATASET --target TARGET [--test TEST_DATASET] [--format json|markdown|html|all] [--output-dir reports]
```

Important options:

- `--target`: target column name.
- `--test`: optional test dataset for train/test checks.
- `--format`: report artifact format. Default is `json`.
- `--output-dir`: output directory. Default is `reports`.

Examples:

```bash
dqa audit examples/datasets/classification_dirty.csv --target label --format all
dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all
```

Output files:

- `reports/audit.json`
- `reports/audit_report.md` when Markdown or all is requested
- `reports/audit_report.html` when HTML or all is requested

## `dqa report`

Purpose: regenerate reports from deterministic audit JSON.

Syntax:

```bash
dqa report AUDIT_JSON --format json|markdown|html|all [--output-dir reports]
```

Example:

```bash
dqa report reports/audit.json --format html
```

Output files:

- `reports/audit_report.json`
- `reports/audit_report.md`
- `reports/audit_report.html`

## `dqa summary`

Purpose: print a compact summary from existing deterministic audit JSON without
rerunning checks.

Syntax:

```bash
dqa summary AUDIT_JSON [--format text|json]
```

Example:

```bash
dqa summary reports/audit.json --format json
```

Output: terminal text or machine-readable JSON.

## `dqa contract`

Purpose: generate a deterministic YAML data contract from an observed dataset.

Syntax:

```bash
dqa contract DATASET --target TARGET [--output-dir contracts] [--filename NAME.yaml]
```

Example:

```bash
dqa contract examples/datasets/classification_dirty.csv --target label
```

Output file:

- `contracts/classification_dirty_contract.yaml`

## `dqa validate`

Purpose: validate a dataset against a generated YAML contract.

Syntax:

```bash
dqa validate DATASET --contract CONTRACT [--output-dir reports]
```

Example:

```bash
dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml
```

Output file:

- `reports/validation_result.json`

## `dqa review`

Purpose: generate a guarded AI-assisted review from deterministic audit JSON.

Syntax:

```bash
dqa review AUDIT_JSON [--provider mock] [--workflow provider|graph] [--output-dir reports]
```

Examples:

```bash
dqa review reports/audit.json --provider mock
dqa review reports/audit.json --provider mock --workflow graph
```

Output files:

- `reports/ai_review.json`
- `reports/ai_review.md` when `--workflow graph` is used
