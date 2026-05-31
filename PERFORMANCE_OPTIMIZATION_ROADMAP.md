# Performance Optimization Roadmap

## Executive Summary

This document outlines identified performance bottlenecks in the Dataset Quality Auditor and provides a structured approach for implementing optimizations using incremental, tested improvements.

## Identified Performance Issues

### 1. **Inefficient Correlation Matrix Computation** (High Priority)
**Location:** `dataset_quality_auditor/audit/checks/correlation.py`

**Current Implementation:**
```python
corr = df[numeric_features].corr(numeric_only=True).abs()
pairs: list[tuple[str, str, float]] = []
for index, column_a in enumerate(numeric_features):
    for column_b in numeric_features[index + 1 :]:
        value = corr.loc[column_a, column_b]
        if float(value) >= CORRELATION_THRESHOLD:
            pairs.append((column_a, column_b, float(value)))
```

**Problem:**
- Full correlation matrix computation is O(n²) for n features
- Memory overhead: stores entire correlation matrix
- Inefficient for datasets with 100+ numeric columns
- Wasteful pair iteration over pre-computed matrix

**Impact:** 50-200ms overhead on datasets with 100+ numeric features

**Proposed Solution:**
- Compute correlations incrementally (only necessary pairs)
- Use NumPy's dot product vectorization instead of Pandas correlation
- Implement early termination when max issues reached
- Add optional sampling for very wide datasets (1000+ columns)

**Acceptance Criteria:**
- 50% reduction in correlation computation time on 100-column datasets
- Maintain numerical accuracy (within floating-point tolerance)
- All existing tests pass
- New benchmark test added

---

### 2. **Multiple DataFrame Passes in Sequential Checks** (High Priority)
**Location:** `dataset_quality_auditor/audit/engine.py`

**Current Implementation:**
```python
for check in get_default_checks():
    issues.extend(check(train_df, train_profile, context))

for check in get_train_test_checks():
    issues.extend(check(train_df, test_df, train_profile, test_profile, context))
```

**Problem:**
- 10+ checks iterate through the DataFrame independently
- No batching or vectorization
- Repeated type checking, column access, computation
- Linear cascade of I/O operations

**Impact:** 30-50% execution time overhead on large datasets

**Proposed Solution:**
- Implement optional check batching strategy
- Add caching for computed column properties (dtype, nulls, etc.)
- Support parallel check execution where safe
- Add check dependency tracking to minimize redundant operations

**Acceptance Criteria:**
- 20-30% improvement in total audit execution time
- Maintain deterministic results (same issues, same ordering)
- Backward-compatible API
- New metrics added to audit metadata

---

### 3. **Repeated Duplicate Detection** (Medium Priority)
**Location:** `dataset_quality_auditor/audit/profiler.py` (line 50)

**Current Implementation:**
```python
duplicate_row_count = int(df.duplicated().sum())
```

**Problem:**
- Full DataFrame scan for duplicate detection
- Potentially called multiple times
- No early termination option
- Inefficient for wide datasets

**Impact:** 50-200ms on datasets with 1M+ rows and 100+ columns

**Proposed Solution:**
- Cache duplicate results in profiler
- Add sampling option for very large datasets
- Implement early termination at threshold
- Optional use of hash-based deduplication for subset of columns

**Acceptance Criteria:**
- Duplicate detection cached within single audit run
- Results identical to current implementation
- New `profile_dataframe` parameter added for sampling strategy

---

### 4. **Per-Column Unique Value Counting** (Medium Priority)
**Location:** `dataset_quality_auditor/audit/profiler.py` (line 64)

**Current Implementation:**
```python
unique_count = int(series.nunique(dropna=True))
```

**Problem:**
- Sequential computation across all columns
- Repeated for high-cardinality columns
- No early termination when threshold exceeded

**Impact:** 20-100ms on datasets with 1000+ columns

**Proposed Solution:**
- Vectorize unique count computation
- Add early termination flag (stop counting after threshold)
- Implement threshold-based sampling
- Cache results in column profile

**Acceptance Criteria:**
- 30% faster unique count computation on 1000-column datasets
- Maintain accuracy (exact counts, not estimates)
- New profile parameter `exact_unique_counts` (default True)

---

### 5. **Redundant Type Checking in Loops** (Low Priority)
**Location:** Multiple check files (`drift.py`, `correlation.py`, etc.)

**Current Implementation:**
```python
for column in sorted(shared):
    if not (pd.api.types.is_numeric_dtype(train_df[column]) and pd.api.types.is_numeric_dtype(test_df[column])):
        continue
```

**Problem:**
- Type checks repeated unnecessarily
- No caching of dtype information
- Inefficient for repeated iterations

**Impact:** 5-20ms overhead on full audits

**Proposed Solution:**
- Pre-compute and cache dtype information
- Create a utility function `get_numeric_columns()` for reuse
- Add a "column metadata" helper in checks module

**Acceptance Criteria:**
- Type information cached in column profile
- New utility function added and used in 3+ checks
- No change to results

---

### 6. **Groupby + Value Counts for Leakage Detection** (Medium Priority)
**Location:** `dataset_quality_auditor/audit/checks/leakage.py` (line 60)

**Current Implementation:**
```python
for _, group in non_null.groupby("feature"):
    ratios.append(float(group["target"].value_counts(normalize=True).max()))
```

**Problem:**
- Expensive for high-cardinality features (1000+ unique values)
- Quadratic complexity: groupby(n) × value_counts(m)
- No early termination
- Repeated computation for all features

**Impact:** 100-500ms on datasets with high-cardinality categorical features

**Proposed Solution:**
- Implement threshold-based early termination
- Use crosstab instead of groupby for faster computation
- Cache feature cardinality metadata
- Skip check for features with cardinality > threshold

**Acceptance Criteria:**
- 40% faster leakage detection on high-cardinality data
- Same detection accuracy
- New config parameter for cardinality skip threshold

---

### 7. **Type Conversion in Datatype Checks** (Low Priority)
**Location:** `dataset_quality_auditor/audit/checks/datatypes.py` (line 25)

**Current Implementation:**
```python
parse_ratio = float(pd.to_numeric(non_null, errors="coerce").notna().mean())
```

**Problem:**
- Full series conversion to numeric for every categorical column
- Wasteful for columns with low numeric parse ratio
- No early termination

**Impact:** 10-50ms overhead on 100+ categorical columns

**Proposed Solution:**
- Sample-based parsing (check first N values)
- Add early termination at confidence threshold
- Cache parse attempts per column

**Acceptance Criteria:**
- Sample-based approach with 95% accuracy to exact method
- 50% faster execution on high-categorical datasets
- New parameter `datatype_sample_size` (default None = exact)

---

## Implementation Priority Matrix

| Issue | Priority | Effort | Impact | Timeline |
|-------|----------|--------|--------|----------|
| Correlation computation | High | Medium | High | Sprint 1 |
| Multiple passes/check batching | High | High | High | Sprint 1-2 |
| Duplicate detection caching | Medium | Low | Medium | Sprint 1 |
| Unique count vectorization | Medium | Medium | Medium | Sprint 2 |
| Dtype caching | Low | Low | Low | Sprint 2 |
| Leakage groupby optimization | Medium | Medium | Medium | Sprint 2 |
| Datatype sample parsing | Low | Low | Low | Sprint 3 |

## Implementation Steps

### Phase 1: Quick Wins (Low-Risk, High-Impact)
1. **Add profiler caching** for duplicate and unique count results
2. **Implement dtype caching** utility
3. **Add benchmark tests** to measure improvements

### Phase 2: Core Optimizations (Medium-Risk, High-Impact)
1. **Refactor correlation computation** with vectorization
2. **Implement leakage detection optimization** with early termination
3. **Add check execution metrics** to audit metadata

### Phase 3: Advanced Optimizations (Higher-Risk, Lower-Impact)
1. **Optional check parallelization**
2. **Sampling strategies** for very large datasets
3. **Streaming/chunked processing** for memory-constrained environments

## Testing Strategy

### Unit Tests
- Each optimization includes targeted unit tests
- Verify numerical accuracy against current implementation
- Test edge cases (empty datasets, single columns, etc.)

### Regression Tests
- All existing tests must pass
- No change to audit results (issues, scores, ordering)
- Deterministic results verified

### Performance Benchmarks
- New benchmark module: `tests/benchmarks/`
- Measure wall-clock time improvements
- Profile memory usage
- Test on synthetic datasets of varying sizes

### Integration Tests
- Full audit workflow on sample datasets
- Verify end-to-end results unchanged
- Test with multiple dataset sizes

## Configuration and Backward Compatibility

### New Configuration Parameters
```yaml
# In audit config or new performance section
optimization:
  enable_check_batching: true
  enable_dtype_caching: true
  correlation_early_termination: true
  unique_count_early_termination: true
  leakage_cardinality_threshold: 1000
  datatype_sample_size: null  # null = exact, int = sample N
```

### Backward Compatibility Guarantees
- Default configuration maintains current behavior
- All new parameters are optional
- Results identical when optimization flags disabled
- CLI interface unchanged

## Success Metrics

### Performance Targets
- **Small datasets (1K rows × 50 cols):** 5-10% faster
- **Medium datasets (100K rows × 200 cols):** 20-30% faster
- **Large datasets (1M rows × 500 cols):** 40-50% faster
- **Wide datasets (10K rows × 1000+ cols):** 30-40% faster

### Code Quality
- No regression in test coverage
- New code maintains <88 character line length
- Type hints added to new functions
- Docstrings updated

### User Feedback
- Zero regression in existing functionality
- No breaking changes to API
- Performance improvements transparent to users (default on)

## Documentation Updates

- [ ] Update README with performance characteristics
- [ ] Add performance tuning guide to docs/
- [ ] Document new config parameters
- [ ] Add benchmarking instructions to CONTRIBUTING.md
- [ ] Update API documentation

## Risk Assessment

### Potential Risks
1. **Numerical precision loss** in vectorized operations
   - Mitigation: Comprehensive test coverage, tolerance checks
2. **Determinism violations** from optimization changes
   - Mitigation: Regression tests compare results byte-for-byte
3. **Memory usage increase** from caching
   - Mitigation: Profile memory, add optional cache size limits
4. **Breaking changes** in API
   - Mitigation: All changes backward-compatible, feature-flagged

## References

- NumPy Vectorization Guide: https://numpy.org/doc/stable/user/basics.broadcasting.html
- Pandas Performance Tips: https://pandas.pydata.org/docs/user_guide/enhancing.html
- Correlation Optimization Techniques: https://en.wikipedia.org/wiki/Pearson_correlation_coefficient#Algorithmic_efficiency

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-31  
**Status:** Ready for Implementation
