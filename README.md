# Dataset Quality Auditor (DQA)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryamanjmwl/dataset-quality-auditor/actions)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A comprehensive Python library for auditing machine learning datasets** - Detect data quality issues before training your models!

---

## 🚀 What is Dataset Quality Auditor?

Dataset Quality Auditor (DQA) is a professional Python library that automatically analyzes your machine learning datasets for common quality issues and risks. It performs **9 comprehensive checks** and generates beautiful HTML reports with actionable recommendations.

### 🎯 Perfect For:
- **Data Scientists** - Validate datasets before model training
- **ML Engineers** - Catch data issues in CI/CD pipelines
- **Data Analysts** - Understand dataset health and characteristics
- **Teams** - Standardize data quality checks across projects

---

## ✨ Key Features

### 🔍 **9 Quality Checks**
- **Missing Values** - Detect and quantify missing data patterns
- **Outliers** - Identify statistical outliers using IQR method
- **Class Imbalance** - Analyze target distribution imbalances
- **Feature Correlation** - Find highly correlated features (redundancy risk)
- **Target Leakage** - Detect features that directly leak the target
- **High Cardinality** - Identify categorical features with too many unique values
- **Duplicates** - Find exact and near-duplicate rows
- **Train/Test Overlap** - Detect data leakage between train/test sets
- **Data Drift** - Monitor changes in feature distributions

### 📊 **Professional Reporting**
- **Health Score** (0-100) - Overall dataset quality assessment
- **HTML Reports** - Beautiful, interactive reports with charts
- **JSON Output** - Structured data for integration
- **Actionable Insights** - Specific recommendations for each issue

### 🛠️ **Easy to Use**
- **CLI Interface** - Simple command-line usage
- **Python API** - Programmatic access for automation
- **Configuration** - YAML-based configuration for customization
- **Type Safe** - Full type hints throughout

---

## 📦 Installation

### Option 1: Install from GitHub (Recommended)
```bash
pip install git+https://github.com/Aryamanjmwl/dataset-quality-auditor.git
```

### Option 2: Clone and Install Locally
```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor
pip install -e .
```

### Requirements
- Python 3.10 or higher
- Dependencies: pandas, numpy, scikit-learn, jinja2, pyyaml

---

## 🚀 Quick Start

### 1. Basic CLI Usage
```bash
# Audit a CSV file with a target column
python -m dqa audit --data your_data.csv --target target_column

# Use custom configuration
python -m dqa audit --data your_data.csv --target target_column --config my_config.yaml
```

### 2. Python API Usage
```python
from dqa import audit_dataset

# Basic audit
results = audit_dataset('your_data.csv', 'target_column')
print(f"Health Score: {results['health_score']}/100")

# Advanced usage with configuration
from dqa.config import Config
config = Config.from_yaml('config.yaml')
results = audit_dataset('your_data.csv', 'target_column', config=config)
```

### 3. Quick Audit Script
```bash
# Use the included quick audit script
python quick_audit.py your_data.csv target_column
```

---

## 📋 Sample Output

After running an audit, you'll get:

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
   💡 Inspect columns with missingness. Consider imputation strategies.

2. [HIGH] Outliers detected in numeric features
   Detected outliers using IQR method. 3 columns exceed threshold.
   💡 Verify outliers are valid or consider robust scaling.

3. [HIGH] Target leakage detected
   2 features show correlation >0.95 with target.
   💡 Remove these features immediately - they leak the target!

4. [MEDIUM] Class imbalance detected
   Target distribution: {0: 65%, 1: 35%}
   💡 Consider oversampling, undersampling, or class weights.

5. [LOW] Highly correlated features
   Found 2 feature pairs with correlation >0.9.
   💡 Consider feature selection or dimensionality reduction.
```

---

## 📁 Project Structure

```
dataset-quality-auditor/
├── dqa/                    # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── application/      # Application layer
│   │   └── runner.py     # Audit runner
│   ├── domain/           # Domain models
│   │   ├── models.py     # Data models
│   │   └── interfaces.py # Abstract interfaces
│   ├── checks/           # Quality checks
│   │   ├── missing_values.py
│   │   ├── outliers.py
│   │   ├── correlation_risk.py
│   │   └── ... (9 total checks)
│   ├── io/               # Data I/O
│   │   └── csv_loader.py # CSV data loading
│   └── reporting/        # Report generation
│       ├── html_reporter.py
│       └── json_reporter.py
├── examples/             # Sample datasets
│   ├── sample.csv
│   ├── train.csv
│   └── test.csv
├── tests/                # Test suite
├── config.yaml          # Default configuration
├── pyproject.toml       # Package configuration
└── quick_audit.py       # Quick audit script
```

---

## ⚙️ Configuration

Customize audit behavior with `config.yaml`:

```yaml
checks:
  missing_values:
    threshold: 0.05  # Alert if >5% missing
  outliers:
    method: iqr       # iqr or zscore
    multiplier: 1.5   # IQR multiplier
  correlation:
    threshold: 0.9    # Alert if correlation >0.9

reporting:
  output_dir: reports/
  formats: [html, json]
```

---

## 📊 Understanding Results

### Health Score Interpretation
- **80-100**: Excellent - Dataset ready for modeling
- **60-79**: Good - Minor issues to address
- **40-59**: Fair - Significant issues need attention
- **20-39**: Poor - Major quality problems
- **0-19**: Critical - Dataset needs major cleanup

### Issue Severity Levels
- **HIGH** 🚨 - Critical issues that will impact model performance
- **MEDIUM** ⚠️ - Important issues that should be addressed
- **LOW** ℹ️ - Minor issues or informational findings

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/Aryamanjmwl/dataset-quality-auditor.git
cd dataset-quality-auditor
pip install -e ".[dev]"
pytest tests/
```

### Adding New Checks
1. Create new check in `dqa/checks/`
2. Implement the check interface
3. Add to `dqa/checks/__init__.py`
4. Update configuration
5. Add tests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with ❤️ for the data science community. Special thanks to the scikit-learn, pandas, and open-source ML communities.

---

## 📞 Support

- 📖 [Getting Started Guide](GETTING_STARTED.md)
- 🚀 [Quick Use Guide](QUICK_USE.md)
- 🐛 [Report Issues](https://github.com/Aryamanjmwl/dataset-quality-auditor/issues)
- 📧 Security issues: See [SECURITY.md](SECURITY.md)

---

**Ready to audit your datasets?** 🚀

```bash
pip install git+https://github.com/Aryamanjmwl/dataset-quality-auditor.git
python -m dqa audit --data your_data.csv --target target_column
```
