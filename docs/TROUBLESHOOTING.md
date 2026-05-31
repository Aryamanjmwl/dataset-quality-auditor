# Troubleshooting Guide

## Common Errors & Solutions

### Error: "Target column not found"

**Symptom:**
```
ValueError: Target column 'label' was not found in dataset.
```

**Causes:**
- Column name doesn't exist in dataset
- Case mismatch (Python is case-sensitive)
- Column name has leading/trailing whitespace

**Solutions:**
1. Verify column name is correct:
   ```bash
   # Check available columns
   head -n 1 your_data.csv
   ```

2. Use exact column name:
   ```bash
   dqa audit data.csv --target converted  # exact match required
   ```

3. Check for whitespace:
   ```bash
   # If column name has spaces, quote it
   dqa audit data.csv --target "Converted Status"
   ```

---

### Error: "Dataset path does not exist"

**Symptom:**
```
FileNotFoundError: Dataset path does not exist or is not a file: data.csv
```

**Causes:**
- File path incorrect
- File doesn't exist at specified location
- Relative path issue

**Solutions:**
```bash
# Use absolute path
dqa audit /full/path/to/data.csv --target label

# Or from correct directory
cd /path/to/data
dqa audit data.csv --target label

# Check file exists
ls -la data.csv
```

---

### Error: "CSV parsing failed"

**Symptom:**
```
ParserError: error tokenizing data
```

**Causes:**
- CSV is malformed (unmatched quotes, wrong delimiter)
- Encoding issue (non-UTF-8 characters)
- File is not actually CSV

**Solutions:**
```bash
# Check if file is valid CSV
head -n 5 data.csv | cat -A  # Show control characters

# Try different encodings
iconv -f ISO-8859-1 -t UTF-8 data.csv > data_utf8.csv

# Validate delimiter
head -n 1 data.csv  # Should show comma-separated columns

# Fix common issues
# - Remove extra carriage returns
# - Fix quote escaping
# - Ensure consistent column count
```

---

### Error: "MemoryError" or "Killed"

**Symptom:**
```
MemoryError: Unable to allocate X.XX GiB for an array...
Killed (process died due to out of memory)
```

**Causes:**
- Dataset too large (1GB+)
- Many columns (1000+)
- Insufficient RAM

**Solutions:**

1. **Check dataset size:**
   ```bash
   ls -lh data.csv  # File size
   wc -l data.csv   # Row count
   head -n 1 data.csv | tr ',' '\n' | wc -l  # Column count
   ```

2. **Sample the dataset:**
   ```bash
   # Keep only first 100K rows
   head -n 100001 large_data.csv > data_sample.csv
   dqa audit data_sample.csv --target label
   ```

3. **Reduce columns:**
   ```bash
   # Keep only important columns
   cut -d',' -f1,2,3,4,5 large_data.csv > data_subset.csv
   dqa audit data_subset.csv --target label
   ```

4. **Increase available memory:**
   ```bash
   # On Linux/Mac
   ulimit -v unlimited
   dqa audit data.csv --target label
   ```

5. **Use system with more RAM:**
   - Maximum tested: 1M rows × 500 columns
   - For larger datasets, contact maintainers

---

### Error: "No issues found but score is low"

**Why this happens:**
- Score deductions are cumulative
- Multiple INFO-level issues add up
- Requires human review counts against score

**Check what triggered it:**
```bash
# View detailed audit JSON
cat reports/audit.json | python -m json.tool

# Look at 'issues' array
# Each issue has 'severity' and 'deduction' amount
```

**Solution:**
- Review the issues array in audit.json
- Address top-severity issues first
- Re-run audit to see score improve

---

### Error: "Output directory is not writable"

**Symptom:**
```
PermissionError: Permission denied: 'reports'
```

**Solutions:**
```bash
# Check permissions
ls -ld reports/

# Fix permissions
chmod 755 reports/

# Or specify writable directory
dqa audit data.csv --target label --output-dir /tmp/audit_results

# Or use current directory
dqa audit data.csv --target label --output-dir .
```

---

### Error: "Invalid config YAML"

**Symptom:**
```
YAMLError: expected '<document start>', but found '...'
```

**Causes:**
- YAML syntax error
- Invalid indentation
- Unquoted strings with special characters

**Solutions:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Common mistakes to fix:
# ✗ missing_threshold: 0.10  (indentation off)
# ✓ missing_threshold: 0.10  (correct indentation)

# ✗ high_cardinality_threshold: 50%  (unquoted special char)
# ✓ high_cardinality_threshold: 0.50  (use decimal)

# Example valid config
missing_warning_threshold: 0.10
missing_critical_threshold: 0.40
duplicate_warning_threshold: 0.01
```

---

## Performance Tuning

### Audit is slow (>5 seconds on 100K rows)

**Optimization tips:**

1. **Reduce dataset size:**
   ```bash
   # Sample first 50K rows
   head -n 50001 large_data.csv > sample.csv
   dqa audit sample.csv --target label
   ```

2. **Profile to find bottleneck:**
   ```bash
   python -m cProfile -s cumtime -m dataset_quality_auditor.cli audit data.csv --target label 2>&1 | head -20
   ```

3. **Check for high-cardinality columns:**
   - These trigger expensive checks
   - Consider dropping ID-like columns before audit

4. **Use config with higher thresholds:**
   ```yaml
   # Skip expensive checks for large datasets
   high_cardinality_threshold: 0.99  # Only flag extreme cardinality
   ```

---

## FAQ

### Q: How do I know if my dataset is ready for training?

**A:** Check the score band:
- **Ready (≥85):** Safe to proceed
- **Needs Attention (60-84):** Review issues, plan mitigations
- **High Risk (<60):** Fix critical issues before training

See the audit report for specific issues and recommendations.

---

### Q: Can I add custom checks?

**A:** Yes! See [docs/ADDING_CHECKS.md](ADDING_CHECKS.md) for instructions.

---

### Q: What's the difference between a Warning and a Critical issue?

**A:**
- **Critical:** Likely to cause training failure (e.g., 50% missing values)
- **Warning:** May impact model performance (e.g., class imbalance)
- **Info:** Informational, low impact (e.g., extra test columns)

Each has different score deductions.

---

### Q: Can I use this for production data validation?

**A:** Partially. Dataset Quality Auditor is designed for ML-readiness auditing, not runtime validation.

For production use:
- Use for pre-training validation ✓
- Use for periodic dataset health checks ✓
- Use for real-time inference validation ✗ (too slow)

For runtime validation, consider Great Expectations or Pandera.

---

### Q: How do I validate a contract?

**A:**
```bash
# Generate contract from reference dataset
dqa contract reference_data.csv --target converted > reference.yaml

# Validate new dataset against contract
dqa validate new_data.csv --contract reference.yaml
```

---

### Q: Can I run this in CI/CD?

**A:** Yes! Use the gate command:
```bash
# Fail if score < 80 or critical issues > 0
dqa audit data.csv --target label
dqa gate reports/audit.json --min-score 80 --max-critical 0

echo $?  # Exit code 0 if passed, 1 if failed
```

---

## Getting Help

1. **Check this guide** for your specific error
2. **Review example outputs** in `examples/reports/`
3. **Check audit.json** for detailed issue information
4. **Open an issue** on GitHub with:
   - Command you ran
   - Error message
   - Dataset size (rows × columns)
   - Sample of first few rows (sanitized)
