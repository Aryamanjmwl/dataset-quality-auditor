# Dataset Quality Auditor (DQA)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Dataset Quality Auditor (DQA)** is a Python library for validating tabular machine learning datasets before training. It detects data issues, measures dataset health, and generates readable JSON and HTML reports.

---

## 🚀 What DQA Does

DQA helps you find data quality and model risk issues in tabular datasets. It runs a set of standard checks, then creates a health score and actionable findings so you can fix problems early.

### Why use DQA?
- Find dataset problems before training a model
- Prevent bad predictions caused by noisy or leaked data
- Standardize dataset validation in your workflow
- Generate reports for data reviews and audits

---

## ✨ Features

### 🔍 Built-in Quality Checks
- **Missing Values** — spots missing data and columns with excessive nulls
- **Outliers** — finds anomalies using IQR method
- **Class Imbalance** — evaluates target distribution imbalance
- **Feature Correlation** — identifies redundant or highly correlated features
- **Target Leakage** — detects features that may leak label information
- **High Cardinality** — flags categorical features with too many unique values
- **Duplicates** — finds identical or duplicate rows
- **Train/Test Overlap** — detects data leakage between train and test sets
- **Data Drift** — compares distribution changes across datasets

### 📊 Reporting
- **Health Score** (0–100)
- **HTML reports** with clean formatting
- **JSON output** for automation and integration
- **Actionable recommendations** for each issue

### 🛠️ Ease of Use
- **CLI** for fast audits
- **Python API** for integration into scripts
- **YAML configuration** for custom behavior
- **Modular design** for easy extension

---

## 📦 Installation

### Option 1: Install from GitHub
```bash
pip install git+https://github.com/Aryamanjmwl/dataset-quality-auditor.git
```

### Option 2: Clone and install locally
```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor
pip install -e .
```

### Requirements
- Python 3.10+
- pandas
- numpy
- scikit-learn
- jinja2
- pyyaml

---

## 🚀 Quick Start

### Basic CLI
```bash
python -m dqa audit --data your_data.csv --target target_column
```

### CLI with config
```bash
python -m dqa audit --data your_data.csv --target target_column --config config.yaml
```

### Python API
```python
from dqa import audit_dataset
from dqa.config import Config

config = Config.from_yaml('config.yaml')
results = audit_dataset('your_data.csv', 'target_column', config=config)
print(f"Health Score: {results['health_score']}/100")
```

### Quick audit script
```bash
python quick_audit.py your_data.csv target_column
```

---

## 📋 Example Output

```
🔍 Starting Data Quality Audit...
📁 File: examples/sample.csv
🎯 Target: target
--------------------------------------------------
📊 AUDIT RESULTS
Health Score: 46.0/100
Dataset: 1000 rows, 15 columns
Issues Found: 5

🚨 ISSUES FOUND:
1. [MEDIUM] Missing values detected
   Dataset contains missing values. Overall missing ratio is 0.023.
   💡 Inspect columns with missingness and consider imputation.

2. [HIGH] Outliers detected in numeric features
   Detected outliers using IQR method. 3 columns exceed threshold.
   💡 Verify whether outliers are valid or apply robust scaling.

3. [HIGH] Target leakage detected
   2 features show correlation >0.95 with target.
   💡 Remove these features or revise feature engineering.

4. [MEDIUM] Class imbalance detected
   Target distribution: {0: 65%, 1: 35%}
   💡 Consider resampling or class weights.

5. [LOW] Highly correlated features
   Found 2 pairs with correlation >0.9.
   💡 Consider feature selection or dimensionality reduction.
```

---

## 📁 Project Structure

```
dataset-quality-auditor/
├── dqa/                    # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── application/        # Audit runner and workflow
│   │   └── runner.py
│   ├── domain/             # Data models and interfaces
│   │   ├── models.py
│   │   └── interfaces.py
│   ├── checks/             # Built-in dataset checks
│   │   ├── missing_values.py
│   │   ├── outliers.py
│   │   ├── correlation_risk.py
│   │   └── ...
│   ├── io/                 # CSV loading
│   │   └── csv_loader.py
│   └── reporting/          # Report generation
│       ├── html_reporter.py
│       └── json_reporter.py
├── examples/               # Sample datasets
│   ├── sample.csv
│   ├── train.csv
│   └── test.csv
├── tests/                  # Test suite
├── config.yaml             # Default configuration
├── pyproject.toml          # Package configuration
└── quick_audit.py          # Quick audit helper script
```

---

## ⚙️ Configuration

Use `config.yaml` to customize checks and output:

```yaml
checks:
  missing_values:
    threshold: 0.05
  outliers:
    method: iqr
    multiplier: 1.5
  correlation:
    threshold: 0.9

reporting:
  output_dir: reports/
  formats: [html, json]
```

---

## 📊 Result Interpretation

### Health score
- **80-100**: Excellent — ready for modeling
- **60-79**: Good — minor improvements suggested
- **40-59**: Fair — significant issues need attention
- **20-39**: Poor — dataset quality is weak
- **0-19**: Critical — dataset requires cleanup

### Severity levels
- **HIGH** 🚨 — fix before modeling
- **MEDIUM** ⚠️ — important but not blocking
- **LOW** ℹ️ — informative or optional

---

## 🧪 Development

```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor
pip install -e "[dev]"
pytest tests/
```

---

## 🛠️ Contributing

1. Add new check under `dqa/checks/`
2. Register it in `dqa/checks/__init__.py`
3. Update `config.yaml` if needed
4. Add tests in `tests/`

---

## 📄 License

MIT License — see [LICENSE](LICENSE).


1. Add new check under `dqa/checks/`
2. Register it in `dqa/checks/__init__.py`
3. Update `config.yaml` if needed
4. Add tests in `tests/`

---

## 📄 License

MIT License — see [LICENSE](LICENSE).
