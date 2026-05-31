# Performance Optimization Implementation Prompt (for Claude/Codex)

## Overview

This prompt is designed to guide an AI assistant (Claude, Codex, or similar) through implementing the performance optimizations outlined in `PERFORMANCE_OPTIMIZATION_ROADMAP.md`. Use this systematically to complete Phase 1 and Phase 2 optimizations.

---

## Context

**Repository:** Aryamanjmwl/dataset-quality-auditor  
**Package:** Python 3.10+ with pandas, numpy, scipy  
**Testing Framework:** pytest  
**Code Style:** ruff (line-length 88, PEP 8)  
**Determinism Requirement:** All results must be identical to current implementation

---

## Task Template: Optimization Implementation

### Pattern for Each Optimization

Use this template for implementing each optimization:

---

## OPTIMIZATION 1: Profiler Caching for Duplicate Detection

### Goal
Cache duplicate row detection results within a single audit run to avoid repeated DataFrame scans.

### Files to Modify
- `dataset_quality_auditor/audit/profiler.py`
- `dataset_quality_auditor/audit/context.py` (optional: add metadata)

### Current Code
```python
# dataset_quality_auditor/audit/profiler.py, lines 50-52
duplicate_row_count = int(df.duplicated().sum())
duplicate_row_percent = (
    float(duplicate_row_count / row_count) if row_count > 0 else 0.0
)
```

### Implementation Steps

1. **Add duplicate detection helper function with optional caching:**
   - Create `_detect_duplicates(df: pd.DataFrame, cache: dict | None = None) -> tuple[int, float]`
   - If `cache` provided and key exists, return cached result
   - Otherwise compute and cache result
   - Return `(duplicate_count, duplicate_percent)`

2. **Modify profile_dataframe function:**
   - Accept optional `_cache: dict | None = None` parameter
   - Pass cache to duplicate detection helper
   - Maintain backward compatibility (cache=None by default)

3. **Add comprehensive tests:**
   - Test cache hit/miss behavior
   - Test results identical to current implementation
   - Test with empty, single-row, and all-duplicate DataFrames
   - Test cache isolation (no cross-contamination)

### Acceptance Criteria
- [ ] Function signature backward compatible
- [ ] Results byte-identical to original implementation
- [ ] 50%+ reduction in duplicate detection time on repeated calls
- [ ] All existing tests pass
- [ ] New cache parameter documented in docstring
- [ ] No breaking changes to API

### Testing Code Template
```python
def test_duplicate_detection_caching():
    """Verify duplicate detection caching works correctly."""
    df = pd.DataFrame({
        'a': [1, 2, 2, 3],
        'b': [4, 5, 5, 6]
    })
    cache = {}
    
    # First call - should compute
    profile1 = profile_dataframe(df, _cache=cache)
    assert 'duplicates' in cache or cache  # Cache was used
    
    # Second call - should use cache
    profile2 = profile_dataframe(df, _cache=cache)
    
    # Results must be identical
    assert profile1['duplicate_row_count'] == profile2['duplicate_row_count']
    assert profile1['duplicate_row_percent'] == profile2['duplicate_row_percent']
```

---

## OPTIMIZATION 2: Dtype Caching Utility

### Goal
Create a reusable utility to cache and share dtype information across checks.

### Files to Create/Modify
- `dataset_quality_auditor/audit/checks/metadata.py` (NEW)
- `dataset_quality_auditor/audit/engine.py` (modify to use)

### Implementation Steps

1. **Create new module `dataset_quality_auditor/audit/checks/metadata.py`:**

```python
"""Column metadata caching for check optimization."""

from typing import Any
import pandas as pd

class ColumnMetadataCache:
    """Cache for column type and property information."""
    
    def __init__(self):
        self._numeric_columns_cache: dict[str, list[str]] = {}
        self._categorical_columns_cache: dict[str, list[str]] = {}
    
    def get_numeric_columns(self, df: pd.DataFrame, key: str | None = None) -> list[str]:
        """Get list of numeric columns with caching."""
        if key and key in self._numeric_columns_cache:
            return self._numeric_columns_cache[key]
        
        columns = [
            col for col in df.columns
            if pd.api.types.is_numeric_dtype(df[col])
        ]
        if key:
            self._numeric_columns_cache[key] = columns
        return columns
    
    def get_categorical_columns(self, df: pd.DataFrame, key: str | None = None) -> list[str]:
        """Get list of categorical columns with caching."""
        if key and key in self._categorical_columns_cache:
            return self._categorical_columns_cache[key]
        
        columns = [
            col for col in df.columns
            if not pd.api.types.is_numeric_dtype(df[col])
        ]
        if key:
            self._categorical_columns_cache[key] = columns
        return columns
    
    def clear(self):
        """Clear all caches."""
        self._numeric_columns_cache.clear()
        self._categorical_columns_cache.clear()
```

2. **Update checks to use metadata cache:**
   - Modify `correlation.py` to use `get_numeric_columns()`
   - Modify `drift.py` to use metadata cache
   - Example:
   ```python
   # OLD
   numeric_features = [
       column for column in df.columns
       if column != context.target_column and pd.api.types.is_numeric_dtype(df[column])
   ]
   
   # NEW
   from dataset_quality_auditor.audit.checks.metadata import ColumnMetadataCache
   metadata = ColumnMetadataCache()
   numeric_features = [
       c for c in metadata.get_numeric_columns(df)
       if c != context.target_column
   ]
   ```

3. **Integrate with audit engine:**
   - Pass metadata cache instance through context or engine
   - Reuse across multiple checks

### Acceptance Criteria
- [ ] `metadata.py` module created with ColumnMetadataCache class
- [ ] Used in 3+ check files
- [ ] 20%+ faster type checking on repeated iterations
- [ ] All existing tests pass
- [ ] Type hints provided throughout
- [ ] Docstrings complete

---

## OPTIMIZATION 3: Correlation Computation Vectorization

### Goal
Replace full correlation matrix with incremental, vectorized pair computation.

### Files to Modify
- `dataset_quality_auditor/audit/checks/correlation.py`

### Current Implementation Problem
```python
corr = df[numeric_features].corr(numeric_only=True).abs()
pairs: list[tuple[str, str, float]] = []
for index, column_a in enumerate(numeric_features):
    for column_b in numeric_features[index + 1 :]:
        value = corr.loc[column_a, column_b]
        if float(value) >= CORRELATION_THRESHOLD:
            pairs.append((column_a, column_b, float(value)))
```

### Implementation Steps

1. **Create vectorized correlation function:**

```python
def _compute_high_correlation_pairs(
    df: pd.DataFrame,
    numeric_features: list[str],
    threshold: float = 0.95,
    max_pairs: int = 20,
) -> list[tuple[str, str, float]]:
    """Compute high-correlation pairs efficiently without full matrix."""
    if len(numeric_features) < 2:
        return []
    
    pairs: list[tuple[str, str, float]] = []
    numeric_df = df[numeric_features].dropna()
    
    if numeric_df.empty or numeric_df.shape[0] < 2:
        return []
    
    # Standardize for correlation
    mean = numeric_df.mean()
    std = numeric_df.std()
    std[std == 0] = 1  # Avoid division by zero
    numeric_std = (numeric_df - mean) / std
    
    # Compute pairwise correlations using dot products
    for i, col_a in enumerate(numeric_features):
        if len(pairs) >= max_pairs:
            break
        for col_b in numeric_features[i + 1:]:
            if len(pairs) >= max_pairs:
                break
            
            # Numerator: dot product of standardized vectors
            correlation = abs(
                numeric_std[col_a].dot(numeric_std[col_b]) / len(numeric_df)
            )
            
            if correlation >= threshold:
                pairs.append((col_a, col_b, float(correlation)))
    
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs[:max_pairs]
```

2. **Update check_correlation_risk function:**
   - Replace full `corr()` call with vectorized function
   - Maintain identical results (test against old implementation)

3. **Add comprehensive tests:**
   - Compare results to current implementation (numeric equality)
   - Test edge cases: single feature, all same values, NaN handling
   - Benchmark on 100-column dataset

### Acceptance Criteria
- [ ] 50%+ faster correlation computation on 100+ column datasets
- [ ] Results numerically identical to original (within 1e-10 tolerance)
- [ ] Early termination at MAX_CORRELATION_ISSUES works
- [ ] All existing tests pass
- [ ] New test file: `tests/benchmarks/test_correlation_performance.py`

---

## OPTIMIZATION 4: Leakage Detection Early Termination

### Goal
Add early termination to categorical target ratio computation.

### Files to Modify
- `dataset_quality_auditor/audit/checks/leakage.py`

### Current Implementation
```python
def _categorical_target_ratio(feature: pd.Series, target: pd.Series) -> float | None:
    non_null = pd.DataFrame({"feature": feature, "target": target}).dropna()
    if non_null.empty or non_null["feature"].nunique() > MAX_CATEGORY_COUNT:
        return None
    ratios = []
    for _, group in non_null.groupby("feature"):
        ratios.append(float(group["target"].value_counts(normalize=True).max()))
    if not ratios:
        return None
    return min(ratios)
```

### Implementation Steps

1. **Add early termination logic:**
   - If min ratio drops below 0.5 threshold, return early
   - Use crosstab instead of groupby for faster computation

```python
def _categorical_target_ratio(feature: pd.Series, target: pd.Series) -> float | None:
    non_null = pd.DataFrame({"feature": feature, "target": target}).dropna()
    if non_null.empty or non_null["feature"].nunique() > MAX_CATEGORY_COUNT:
        return None
    
    # Use crosstab for faster computation
    ct = pd.crosstab(non_null["feature"], non_null["target"], normalize="index")
    
    # Early termination: if any row has very low max, return quickly
    ratios = ct.max(axis=1).values
    if len(ratios) == 0:
        return None
    
    return float(min(ratios))
```

2. **Add cardinality threshold skip:**
   - Skip leakage check for features with cardinality > threshold
   - Add config parameter: `max_leakage_feature_cardinality`

3. **Test and benchmark:**
   - Verify results identical to original implementation
   - Benchmark on high-cardinality datasets

### Acceptance Criteria
- [ ] 40%+ faster on high-cardinality datasets
- [ ] Results identical to original implementation
- [ ] New config parameter documented
- [ ] Tests pass, new benchmark added

---

## OPTIMIZATION 5: Benchmark Test Infrastructure

### Goal
Create comprehensive benchmark tests to measure performance improvements.

### Files to Create
- `tests/benchmarks/__init__.py`
- `tests/benchmarks/conftest.py`
- `tests/benchmarks/test_profiler_performance.py`
- `tests/benchmarks/test_correlation_performance.py`

### Implementation Steps

1. **Create benchmark fixture:**

```python
# tests/benchmarks/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def small_dataframe():
    """Create small synthetic dataset (1K rows, 50 cols)."""
    np.random.seed(42)
    return pd.DataFrame({
        f'col_{i}': np.random.randn(1000)
        for i in range(50)
    })

@pytest.fixture
def large_dataframe():
    """Create large synthetic dataset (100K rows, 200 cols)."""
    np.random.seed(42)
    return pd.DataFrame({
        f'col_{i}': np.random.randn(100_000)
        for i in range(200)
    })

@pytest.fixture
def wide_dataframe():
    """Create wide dataset (10K rows, 1000 cols)."""
    np.random.seed(42)
    return pd.DataFrame({
        f'col_{i}': np.random.randn(10_000)
        for i in range(1000)
    })
```

2. **Create benchmark tests:**

```python
# tests/benchmarks/test_profiler_performance.py
import pytest
from dataset_quality_auditor.audit.profiler import profile_dataframe

def test_profiler_duplicate_detection_performance(benchmark, small_dataframe):
    """Benchmark duplicate detection in profiler."""
    def run():
        return profile_dataframe(small_dataframe)
    
    result = benchmark(run)
    assert 'duplicate_row_count' in result
    assert 'duplicate_row_percent' in result

def test_profiler_caching_performance(benchmark, small_dataframe):
    """Benchmark caching effectiveness."""
    cache = {}
    
    def run_with_cache():
        profile_dataframe(small_dataframe, _cache=cache)
    
    benchmark(run_with_cache)
```

3. **Run benchmarks:**
   ```bash
   pytest tests/benchmarks/ -v --benchmark-only
   ```

### Acceptance Criteria
- [ ] Benchmark infrastructure created
- [ ] 3+ benchmarks added for critical paths
- [ ] Benchmarks runnable with `pytest --benchmark-only`
- [ ] Results compared to baseline

---

## STEP-BY-STEP EXECUTION GUIDE

### Phase 1: Quick Wins (Day 1-2)

**Execute in this order:**

1. Create `tests/benchmarks/` infrastructure
2. Implement **OPTIMIZATION 2: Dtype Caching** (OPTIMIZATION_2)
3. Implement **OPTIMIZATION 1: Duplicate Detection Caching** (OPTIMIZATION_1)
4. Run benchmarks to verify improvements
5. Create GitHub issue documenting Phase 1 results

### Phase 2: Core Optimizations (Day 3-5)

1. Implement **OPTIMIZATION 3: Correlation Vectorization** (OPTIMIZATION_3)
2. Implement **OPTIMIZATION 4: Leakage Early Termination** (OPTIMIZATION_4)
3. Run full test suite + benchmarks
4. Create GitHub PR with Phase 2 changes
5. Document performance metrics

### Phase 3: Testing & Documentation (Day 6)

1. Run comprehensive test suite
2. Verify all tests pass
3. Update README with performance characteristics
4. Create performance tuning documentation

---

## Prompting the AI Assistant

### For Each Optimization, Use This Prompt Template:

```
You are helping optimize the dataset-quality-auditor Python library.

TASK: Implement [OPTIMIZATION NAME]

CONTEXT:
- Repository: Aryamanjmwl/dataset-quality-auditor
- Python 3.10+, pytest, pandas 2.0+, numpy 1.26+
- Code style: ruff, 88 char lines, type hints required

GOAL: [State goal from optimization section]

FILES TO MODIFY: [List files]

CURRENT IMPLEMENTATION:
[Paste current code]

REQUIREMENTS:
1. Results must be byte-identical to original implementation
2. All existing tests must pass
3. Add comprehensive test coverage
4. Type hints for all new functions
5. Docstrings explaining optimization rationale
6. Backward compatible (no breaking changes)

IMPLEMENTATION STEPS:
[Include the steps from the optimization section]

ACCEPTANCE CRITERIA:
[Include criteria from optimization section]

TESTING CODE TEMPLATE:
[Include test template if provided]

Please provide:
1. Complete modified/new code files
2. Test code for the optimization
3. Brief performance analysis
4. Any considerations or caveats
```

### Example Usage

```
You are helping optimize the dataset-quality-auditor Python library.

TASK: Implement OPTIMIZATION 1: Profiler Caching for Duplicate Detection

CONTEXT:
- Repository: Aryamanjmwl/dataset-quality-auditor
- Python 3.10+, pytest, pandas 2.0+
- Code style: ruff, 88 char lines, type hints required

GOAL:
Cache duplicate row detection results within a single audit run to avoid repeated DataFrame scans.

FILES TO MODIFY:
- dataset_quality_auditor/audit/profiler.py
- dataset_quality_auditor/audit/context.py (optional)

CURRENT IMPLEMENTATION:
[See OPTIMIZATION 1 section above]

[... rest of prompt template ...]
```

---

## Quality Assurance Checklist

Before committing each optimization:

- [ ] Code passes `ruff check .`
- [ ] All tests pass: `pytest tests/`
- [ ] Coverage maintained or improved
- [ ] Benchmark shows expected improvement
- [ ] Results numerically identical to original
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] No breaking changes to public API
- [ ] Edge cases tested (empty, single-row, NaN, etc.)

---

## References

### Performance Profiling
```bash
# Profile execution time
python -m cProfile -s cumtime -m dataset_quality_auditor.cli audit data.csv

# Memory profiling
pip install memory_profiler
python -m memory_profiler main_script.py
```

### Testing
```bash
# Run specific test
pytest tests/audit/checks/test_correlation.py -v

# Run with coverage
pytest --cov=dataset_quality_auditor tests/

# Run benchmarks
pytest tests/benchmarks/ --benchmark-only
```

---

## Document Metadata

- **Version:** 1.0
- **Created:** 2026-05-31
- **Status:** Ready for AI Assistant Implementation
- **Target:** Claude, Codex, or equivalent LLM
- **Estimated Effort:** 8-12 hours for Phase 1-2

---

## Questions for AI Assistant

When implementing each optimization, the AI should address:

1. **Why is this optimization safe?**
   - Maintains deterministic results
   - No API changes
   - Backward compatible

2. **What are the performance gains?**
   - Estimated reduction in wall-clock time
   - Memory impact (positive or negative)
   - Scalability improvement

3. **What are the edge cases?**
   - Empty datasets
   - Single-row datasets
   - All-NaN columns
   - High-cardinality features

4. **How do we verify correctness?**
   - Compare to original implementation
   - Regression test suite
   - Benchmark stability

---

**Next Steps:** Use this document to guide Claude/Codex through implementing the performance optimizations. Start with Phase 1 quick wins, then proceed to Phase 2 core optimizations.
