"""Audit configuration loading and validation."""

from __future__ import annotations

from pathlib import Path

import yaml

SUPPORTED_THRESHOLD_KEYS = {
    "numeric_drift": {
        "mean_shift_std_ratio": "numeric_drift_mean_shift_std_ratio",
    },
    "categorical_drift": {
        "dominant_category_shift": "categorical_drift_dominant_category_shift",
        "missing_category_ratio": "categorical_drift_missing_category_ratio",
    },
    "target_distribution_drift": {
        "warning_shift": "target_distribution_drift_warning_shift",
        "critical_shift": "target_distribution_drift_critical_shift",
    },
}


def load_audit_config(path: str | Path | None) -> dict[str, float]:
    """Load supported audit threshold overrides from a YAML file."""
    if path is None:
        return {}

    config_path = Path(path)
    if not config_path.is_file():
        msg = f"Audit config path does not exist or is not a file: {config_path}"
        raise FileNotFoundError(msg)

    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        msg = f"Audit config file did not contain a YAML mapping: {config_path}"
        raise ValueError(msg)

    return parse_audit_config(loaded)


def parse_audit_config(config: dict[str, object]) -> dict[str, float]:
    """Validate and flatten the public audit config shape."""
    unknown_top_level = sorted(set(config) - {"thresholds"})
    if unknown_top_level:
        msg = f"Unsupported audit config key(s): {', '.join(unknown_top_level)}"
        raise ValueError(msg)

    thresholds = config.get("thresholds", {})
    if thresholds is None:
        return {}
    if not isinstance(thresholds, dict):
        msg = "Audit config 'thresholds' must be a mapping."
        raise ValueError(msg)

    flattened: dict[str, float] = {}
    for group_name, group_value in thresholds.items():
        if group_name not in SUPPORTED_THRESHOLD_KEYS:
            msg = f"Unsupported audit threshold group: {group_name}"
            raise ValueError(msg)
        if not isinstance(group_value, dict):
            msg = f"Audit threshold group '{group_name}' must be a mapping."
            raise ValueError(msg)

        supported = SUPPORTED_THRESHOLD_KEYS[group_name]
        for key, value in group_value.items():
            if key not in supported:
                msg = f"Unsupported audit threshold key: {group_name}.{key}"
                raise ValueError(msg)
            flattened[supported[key]] = _as_float(
                value,
                key=f"{group_name}.{key}",
            )

    _validate_threshold_relationships(flattened)
    return flattened


def _as_float(value: object, key: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        msg = f"Audit threshold '{key}' must be a number."
        raise ValueError(msg)
    numeric = float(value)
    if numeric < 0:
        msg = f"Audit threshold '{key}' must be greater than or equal to 0."
        raise ValueError(msg)
    return numeric


def _validate_threshold_relationships(config: dict[str, float]) -> None:
    warning = config.get("target_distribution_drift_warning_shift")
    critical = config.get("target_distribution_drift_critical_shift")
    if warning is not None and critical is not None and critical < warning:
        msg = (
            "Audit threshold 'target_distribution_drift.critical_shift' must be "
            "greater than or equal to warning_shift."
        )
        raise ValueError(msg)
