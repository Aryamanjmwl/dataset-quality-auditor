---
name: Bug Report
about: Report a bug or issue with Dataset Quality Auditor
title: '[BUG] '
labels: 'bug'
assignees: ''

---

## Description

Clear and concise description of the bug.

## Steps to Reproduce

1. Step 1
2. Step 2
3. ...

## Expected Behavior

What should happen?

## Actual Behavior

What actually happened?

## Environment

```bash
# Run and paste output
python --version
pip show pandas numpy
pip show dataset-quality-auditor
```

## Dataset Info

```python
# If possible, provide sample of your dataset
import pandas as pd
df = pd.read_csv('your_data.csv')
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Types:\n{df.dtypes}")
print(f"Missing:\n{df.isnull().sum()}")
```

## Error Output

```
Paste full error message/traceback here
```

## Command Run

```bash
# Exact command that caused the issue
dqa audit your_data.csv --target label --format all
```

## Files

- [ ] Can you share the dataset (or a sample)?
- [ ] Can you share the audit JSON output?
- [ ] Can you share the audit log?

## Additional Context

Any other context?
