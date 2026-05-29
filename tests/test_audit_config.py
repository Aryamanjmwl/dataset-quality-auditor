import pytest

from dataset_quality_auditor.audit.config import parse_audit_config
from dataset_quality_auditor.audit.context import create_audit_context


def test_parse_audit_config_flattens_supported_thresholds() -> None:
    config = parse_audit_config(
        {
            "thresholds": {
                "numeric_drift": {"mean_shift_std_ratio": 0.75},
                "categorical_drift": {
                    "dominant_category_shift": 0.40,
                    "missing_category_ratio": 0.60,
                },
                "target_distribution_drift": {
                    "warning_shift": 0.35,
                    "critical_shift": 0.70,
                },
            }
        }
    )

    assert config == {
        "numeric_drift_mean_shift_std_ratio": 0.75,
        "categorical_drift_dominant_category_shift": 0.40,
        "categorical_drift_missing_category_ratio": 0.60,
        "target_distribution_drift_warning_shift": 0.35,
        "target_distribution_drift_critical_shift": 0.70,
    }


def test_no_config_keeps_default_drift_thresholds() -> None:
    context = create_audit_context("train.csv", target_column="label")

    assert context.config["numeric_drift_mean_shift_std_ratio"] == 1.0
    assert context.config["categorical_drift_dominant_category_shift"] == 0.30
    assert context.config["categorical_drift_missing_category_ratio"] == 0.50
    assert context.config["target_distribution_drift_warning_shift"] == 0.25
    assert context.config["target_distribution_drift_critical_shift"] == 0.50


def test_unknown_config_key_fails_clearly() -> None:
    with pytest.raises(ValueError, match="Unsupported audit threshold key"):
        parse_audit_config(
            {
                "thresholds": {
                    "numeric_drift": {"unsupported": 1.0},
                }
            }
        )


def test_unknown_top_level_config_key_fails() -> None:
    with pytest.raises(ValueError, match="Unsupported audit config key"):
        parse_audit_config({"thresholds": {}, "mode": "strict"})


def test_unknown_threshold_group_fails() -> None:
    with pytest.raises(ValueError, match="Unsupported audit threshold group"):
        parse_audit_config(
            {
                "thresholds": {
                    "schema_drift": {"missing_column": 1.0},
                }
            }
        )


def test_critical_shift_lower_than_warning_shift_fails() -> None:
    with pytest.raises(ValueError, match="critical_shift"):
        parse_audit_config(
            {
                "thresholds": {
                    "target_distribution_drift": {
                        "warning_shift": 0.50,
                        "critical_shift": 0.25,
                    }
                }
            }
        )


def test_negative_threshold_fails() -> None:
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        parse_audit_config(
            {
                "thresholds": {
                    "numeric_drift": {"mean_shift_std_ratio": -0.1},
                }
            }
        )


def test_boolean_threshold_fails() -> None:
    with pytest.raises(ValueError, match="must be a number"):
        parse_audit_config(
            {
                "thresholds": {
                    "target_distribution_drift": {"warning_shift": True},
                }
            }
        )


def test_non_numeric_threshold_fails() -> None:
    with pytest.raises(ValueError, match="must be a number"):
        parse_audit_config(
            {
                "thresholds": {
                    "categorical_drift": {"missing_category_ratio": "high"},
                }
            }
        )
