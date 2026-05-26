#!/usr/bin/env python3
"""
Quick DQA Script for Heart Disease Data
Usage: python quick_audit.py heart_disease.csv
"""

import sys
import pandas as pd
from pathlib import Path


def quick_audit(csv_file, target_col="target"):
    """Simple function to audit heart disease data"""

    try:
        # Import DQA
        from dqa import AuditRunner, CSVDataLoader
        from dqa.checks import (
            MissingValuesCheck,
            ClassImbalanceCheck,
            OutlierDetectionCheck,
            TargetLeakageCheck,
            CorrelationRiskCheck,
        )

        print("🔍 Starting Data Quality Audit...")
        print(f"📁 File: {csv_file}")
        print(f"🎯 Target: {target_col}")
        print("-" * 50)

        # Create auditor with heart disease relevant checks
        auditor = AuditRunner(
            checks=[
                MissingValuesCheck(),
                ClassImbalanceCheck(),
                OutlierDetectionCheck(),
                TargetLeakageCheck(),
                CorrelationRiskCheck(),
            ],
            loader=CSVDataLoader(),
        )

        # Run audit
        report = auditor.audit_csv(csv_file, target=target_col)

        # Print results
        print("📊 AUDIT RESULTS")
        print(f"Health Score: {report.health_score}/100")
        print(f"Dataset: {report.dataset.n_rows} rows, {report.dataset.n_cols} columns")
        print(f"Issues Found: {len(report.findings)}")
        print()

        if report.findings:
            print("🚨 ISSUES FOUND:")
            for i, finding in enumerate(report.findings, 1):
                print(f"{i}. [{finding.severity.value}] {finding.title}")
                print(f"   {finding.description}")
                if finding.recommendation:
                    print(f"   💡 {finding.recommendation}")
                print()
        else:
            print("✅ NO ISSUES FOUND - Your data looks great!")

        # Quick data summary
        print("📈 DATA SUMMARY:")
        try:
            df = pd.read_csv(csv_file)
            print(f"Target distribution: {df[target_col].value_counts().to_dict()}")
            print(".2f")
            print(f"Missing values: {df.isnull().sum().sum()} total")
        except Exception as e:
            print(f"Could not load data summary: {e}")

        return report

    except ImportError:
        print("❌ ERROR: DQA not installed!")
        print(
            "Run: pip install git+https://github.com/your-username/dataset-quality-auditor.git"
        )
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_audit.py your_data.csv [target_column]")
        print("Example: python quick_audit.py heart_disease.csv target")
        sys.exit(1)

    csv_file = sys.argv[1]
    target_col = sys.argv[2] if len(sys.argv) > 2 else "target"

    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        sys.exit(1)

    quick_audit(csv_file, target_col)
