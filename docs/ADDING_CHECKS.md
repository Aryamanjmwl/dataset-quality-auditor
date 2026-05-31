# Adding Custom Checks

This guide explains how to add new data quality checks to Dataset Quality Auditor.

## Overview

Checks are deterministic functions that analyze a dataset and return a list of `Issue` objects. Each check:
- Takes input data and produces issues
- Must be **deterministic** (same input → same output)
- Should have **clear passing/failing criteria**
- Must include **reproducible evidence**

---

## Check Template

### Single-Dataset Check

```python
# File: dataset_quality_auditor/audit/checks/my_check.py

from dataclasses import dataclass
from typing import Any

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, WARNING, INFO, HIGH, MEDIUM, LOW


def check_my_data_quality_issue(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Check for my custom data quality issue.
    
    This function is deterministic: same input always produces same output.
    
    Args:
        df: Input DataFrame to check
        profile: Pre-computed profile (from profiler.py)
        context: Audit context with configuration and metadata
    
    Returns:
        List of Issue objects (empty if no issues found)
    
    Notes:
        - Must be deterministic (no randomness, external calls, timestamps)
        - Return empty list if no issues found
        - All numeric values must be JSON-serializable
    """
    issues: list[Issue] = []
    
    # Early exit if not applicable
    if len(df) == 0:
        return issues
    
    # Extract configuration
    threshold = context.config.get('my_check_threshold', 0.10)
    
    # Perform analysis
    problematic_columns = []
    for column in df.columns:
        if column == context.target_column:
            continue  # Skip target column
        
        # Compute metric
        metric_value = compute_my_metric(df[column])
        
        # Check against threshold
        if metric_value >= threshold:
            problematic_columns.append((
                column,
                metric_value,
                threshold,
            ))
    
    # Create issues
    for column, observed_value, threshold in sorted(problematic_columns):
        issues.append(
            Issue(
                issue_id=issue_id('my_check', column),
                check_id='my_check',
                title='Description of the issue',
                severity=WARNING,  # or CRITICAL, INFO
                risk_level=MEDIUM,  # or HIGH, LOW
                status='failed',
                scope={
                    'dataset': 'train',
                    'column': column,
                    'column_role': 'feature',
                },
                evidence=Evidence(
                    metric='my_metric_name',
                    observed_value=float(observed_value),
                    threshold=float(threshold),
                    comparison='observed_value >= threshold',
                    details={
                        'column': column,
                        'my_metric': float(observed_value),
                        'threshold': float(threshold),
                        # Add other relevant details
                    },
                ),
                ml_impact=(
                    'Explain how this issue impacts model training. '
                    'Be specific and actionable.'
                ),
                recommendation=(
                    'Provide specific, actionable recommendation. '
                    'E.g., "Remove rows with X" or "Impute using Y strategy".'
                ),
                requires_human_review=False,  # Set True if ambiguous
                reproducibility=reproducibility(
                    context,
                    {'my_check_threshold': threshold},
                ),
            )
        )
    
    return issues


def compute_my_metric(series: pd.Series) -> float:
    """Compute the metric for a single column.
    
    This must be deterministic.
    
    Args:
        series: Column to analyze
    
    Returns:
        Metric value (0-1 range recommended)
    """
    # Your analysis logic here
    return float(series.isna().sum() / len(series)) if len(series) > 0 else 0.0
```

### Train/Test Check (Comparative)

```python
def check_train_test_data_quality(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Compare train and test datasets for quality issues.
    
    Args:
        train_df: Training dataset
        test_df: Test dataset
        train_profile: Pre-computed training profile
        test_profile: Pre-computed test profile
        context: Audit context
    
    Returns:
        List of issues found
    """
    issues: list[Issue] = []
    
    # Compare distributions, schemas, etc.
    for column in train_df.columns:
        if column not in test_df.columns:
            issues.append(Issue(...))
    
    return issues
```

---

## Step-by-Step Implementation

### Step 1: Create Check Function

1. Create new file: `dataset_quality_auditor/audit/checks/my_check.py`
2. Implement function following template above
3. Ensure it returns `list[Issue]`

### Step 2: Register Check

Add to `dataset_quality_auditor/audit/registry.py`:

```python
from dataset_quality_auditor.audit.checks.my_check import check_my_data_quality_issue

def get_default_checks() -> list[Callable]:
    """Return list of single-dataset checks."""
    return [
        check_missing_values,
        check_duplicate_rows,
        # ... existing checks ...
        check_my_data_quality_issue,  # ADD HERE
    ]

def get_train_test_checks() -> list[Callable]:
    """Return list of train/test comparative checks."""
    return [
        check_schema_mismatch,
        # ... existing checks ...
        # ADD TRAIN/TEST CHECKS HERE
    ]
```

### Step 3: Write Tests

Create `tests/audit/checks/test_my_check.py`:

```python
import pandas as pd
import pytest

from dataset_quality_auditor.audit.checks.my_check import check_my_data_quality_issue
from dataset_quality_auditor.audit.context import create_audit_context


def test_my_check_detects_issue():
    """Verify check detects the issue when present."""
    df = pd.DataFrame({
        'col1': [1.0, 2.0, 3.0, None, None],  # 40% missing
        'col2': ['a', 'b', 'c', 'd', 'e'],
    })
    profile = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': {},
    }
    context = create_audit_context('test.csv', target_column=None)
    
    issues = check_my_data_quality_issue(df, profile, context)
    
    assert len(issues) > 0
    assert issues[0].check_id == 'my_check'
    assert 'col1' in issues[0].scope['column']


def test_my_check_passes_good_data():
    """Verify check passes on good data."""
    df = pd.DataFrame({
        'col1': [1.0, 2.0, 3.0, 4.0, 5.0],  # No missing
        'col2': ['a', 'b', 'c', 'd', 'e'],
    })
    profile = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': {},
    }
    context = create_audit_context('test.csv', target_column=None)
    
    issues = check_my_data_quality_issue(df, profile, context)
    
    assert len(issues) == 0


def test_my_check_empty_dataframe():
    """Verify check handles empty DataFrame."""
    df = pd.DataFrame()
    profile = {'row_count': 0, 'column_count': 0, 'columns': {}}
    context = create_audit_context('test.csv')
    
    issues = check_my_data_quality_issue(df, profile, context)
    
    assert len(issues) == 0


def test_my_check_determinism():
    """Verify check is deterministic."""
    df = pd.DataFrame({
        'col1': [1.0, None, 3.0] * 100,
        'col2': ['a', 'b', 'c'] * 100,
    })
    profile = {'row_count': len(df), 'column_count': len(df.columns), 'columns': {}}
    context = create_audit_context('test.csv')
    
    issues1 = check_my_data_quality_issue(df, profile, context)
    issues2 = check_my_data_quality_issue(df, profile, context)
    
    # Same input → same output
    assert len(issues1) == len(issues2)
    for i1, i2 in zip(issues1, issues2):
        assert i1.issue_id == i2.issue_id
        assert i1.evidence.observed_value == i2.evidence.observed_value
```

### Step 4: Add Configuration (Optional)

To make your check configurable, add to `dataset_quality_auditor/audit/context.py`:

```python
DEFAULT_CONFIG: dict[str, float] = {
    # ... existing config ...
    'my_check_threshold': 0.10,  # ADD THIS
}
```

### Step 5: Run Tests

```bash
pytest tests/audit/checks/test_my_check.py -v
pytest tests/  # Full suite
ruff check dataset_quality_auditor/audit/checks/my_check.py
```

---

## Best Practices

### ✅ DO

- ✅ Keep checks **deterministic** (no randomness, no time-based logic)
- ✅ Return **empty list** if no issues found
- ✅ Use **clear issue IDs** (auto-generated by `issue_id()` function)
- ✅ Provide **specific, actionable recommendations**
- ✅ Include **reproducibility metadata** (thresholds, config)
- ✅ Handle **edge cases** (empty data, all-missing columns, single row)
- ✅ Add **comprehensive tests** (normal case, edge cases, determinism)
- ✅ Use **type hints** throughout
- ✅ Document **impact and recommendations** clearly
- ✅ Early exit for **inapplicable scenarios**

### ❌ DON'T

- ❌ Make non-deterministic checks (random sampling, timestamps)
- ❌ Use external API calls or network requests
- ❌ Modify the DataFrame
- ❌ Use hardcoded thresholds (make configurable)
- ❌ Skip error handling for edge cases
- ❌ Return non-JSON-serializable types
- ❌ Make assumptions about data (validate first)
- ❌ Ignore missing values without explicit handling

---

## Example: Implement a New Check

### Scenario: Detect Constant Columns

```python
# File: dataset_quality_auditor/audit/checks/constants.py

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import INFO, LOW


def check_constant_columns(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Check for columns with only one unique value (constant columns).
    
    Constant columns provide no predictive signal and should be removed.
    """
    issues: list[Issue] = []
    
    for column in df.columns:
        if column == context.target_column:
            continue
        
        # Count unique values (excluding NaN)
        unique_count = df[column].nunique()
        
        if unique_count <= 1:
            issues.append(
                Issue(
                    issue_id=issue_id('constant_column', column),
                    check_id='constant_column',
                    title='Constant column detected',
                    severity=INFO,
                    risk_level=LOW,
                    status='failed',
                    scope={
                        'dataset': 'train',
                        'column': column,
                        'column_role': 'feature',
                    },
                    evidence=Evidence(
                        metric='unique_count',
                        observed_value=int(unique_count),
                        threshold=1,
                        comparison='observed_value <= threshold',
                        details={
                            'column': column,
                            'unique_count': int(unique_count),
                        },
                    ),
                    ml_impact=(
                        'Constant columns have no predictive power and waste '
                        'model capacity.'
                    ),
                    recommendation=(
                        'Remove this column before training. It provides no signal.'
                    ),
                    requires_human_review=False,
                    reproducibility=reproducibility(context, {}),
                )
            )
    
    return issues
```

---

## Testing Your Check

### Run Single Test
```bash
pytest tests/audit/checks/test_my_check.py::test_my_check_detects_issue -v
```

### Run All Tests for Check Module
```bash
pytest tests/audit/checks/test_my_check.py -v
```

### Check Code Quality
```bash
ruff check dataset_quality_auditor/audit/checks/my_check.py
```

### Run Full Suite
```bash
pytest tests/ --cov=dataset_quality_auditor
```

---

## Debugging Tips

### Print Debug Info
```python
# In check function
print(f"Column: {column}, unique: {df[column].nunique()}")
```

### Run Specific Test
```bash
pytest tests/audit/checks/test_my_check.py::test_specific_test -v -s
```

### Check Issue Structure
```python
# In test
issue = issues[0]
print(f"Issue ID: {issue.issue_id}")
print(f"Severity: {issue.severity}")
print(f"Evidence: {issue.evidence.observed_value}")
```

---

## Submitting Your Check

1. Implement check function
2. Add to registry
3. Write comprehensive tests
4. Ensure tests pass: `pytest tests/`
5. Check style: `ruff check .`
6. Create PR with:
   - Check implementation
   - Tests
   - Example output (if applicable)
   - Brief description of what check detects

---

## Questions?

Refer to existing checks in `dataset_quality_auditor/audit/checks/` for more examples.
