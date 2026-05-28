# Public Demo

This demo uses only committed example datasets and local deterministic logic.

```bash
pip install -e ".[dev]"

dqa audit examples/datasets/classification_dirty.csv --target label --format all

dqa audit examples/datasets/train_sample.csv --test examples/datasets/test_sample.csv --target label --format all

dqa contract examples/datasets/classification_dirty.csv --target label

dqa validate examples/datasets/classification_dirty.csv --contract contracts/classification_dirty_contract.yaml

dqa review reports/audit.json --provider mock --workflow graph
```

Expected runtime outputs:

- `reports/audit.json`
- `reports/audit_report.md`
- `reports/audit_report.html`
- `contracts/classification_dirty_contract.yaml`
- `reports/validation_result.json`
- `reports/ai_review.json`
- `reports/ai_review.md`

Generated root `reports/` and `contracts/` directories are ignored by Git.
Curated examples are committed under:

- `examples/reports/`
- `examples/contracts/`
- `examples/validation/`

The AI review command uses the deterministic mock provider only. It does not
call external APIs, require API keys, invent findings, modify scores, or edit
datasets.
