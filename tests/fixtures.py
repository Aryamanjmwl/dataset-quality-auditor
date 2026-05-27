"""Shared test fixtures."""


def sample_audit_result() -> dict[str, object]:
    return {
        "audit_id": "audit-001",
        "created_at": "2026-05-26T20:00:00+00:00",
        "dataset_path": "examples/datasets/classification_dirty.csv",
        "target_column": "label",
        "profile": {
            "row_count": 10,
            "column_count": 3,
            "duplicate_row_count": 1,
            "duplicate_row_percent": 0.1,
            "columns": {
                "customer_id": {
                    "name": "customer_id",
                    "dtype": "object",
                    "inferred_role": "id_candidate",
                    "missing_percent": 0.0,
                    "unique_percent": 0.9,
                    "is_numeric": False,
                    "is_categorical": True,
                },
                "age": {
                    "name": "age",
                    "dtype": "float64",
                    "inferred_role": "feature",
                    "missing_percent": 0.2,
                    "unique_percent": 0.7,
                    "is_numeric": True,
                    "is_categorical": False,
                },
                "label": {
                    "name": "label",
                    "dtype": "int64",
                    "inferred_role": "target",
                    "missing_percent": 0.0,
                    "unique_percent": 0.2,
                    "is_numeric": True,
                    "is_categorical": False,
                },
            },
        },
        "issues": [
            {
                "issue_id": "missing_values_age_001",
                "check_id": "missing_values",
                "title": "Missing values detected in feature column",
                "severity": "warning",
                "risk_level": "medium",
                "status": "failed",
                "scope": {
                    "dataset": "train",
                    "column": "age",
                    "column_role": "feature",
                },
                "evidence": {
                    "metric": "missing_percent",
                    "observed_value": 0.2,
                    "threshold": 0.1,
                    "comparison": "observed_value >= threshold",
                    "details": {"missing_count": 2, "total_rows": 10},
                },
                "ml_impact": "Missing values can make model training unstable.",
                "recommendation": "Handle missing values inside preprocessing.",
                "requires_human_review": False,
                "reproducibility": {
                    "check_version": "0.1.0",
                    "parameters": {"missing_warning_threshold": 0.1},
                },
            }
        ],
        "score": {
            "score": 92,
            "max_score": 100,
            "score_band": "ready",
            "deductions": [
                {
                    "issue_id": "missing_values_age_001",
                    "severity": "warning",
                    "deduction": 8,
                    "reason": "warning issue",
                }
            ],
        },
        "metadata": {
            "package_version": "0.1.0",
            "engine_version": "0.1.0",
            "deterministic": True,
            "ai_generated": False,
        },
    }
