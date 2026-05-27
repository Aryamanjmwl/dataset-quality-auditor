"""Deterministic data contract validation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml


def load_contract(path: str | Path) -> dict[str, object]:
    """Load a YAML data contract."""
    contract_path = Path(path)
    if not contract_path.is_file():
        msg = f"Contract path does not exist or is not a file: {contract_path}"
        raise FileNotFoundError(msg)
    loaded = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        msg = f"Contract file did not contain a YAML mapping: {contract_path}"
        raise ValueError(msg)
    return loaded


def _load_dataset(path: str | Path) -> pd.DataFrame:
    dataset_path = Path(path)
    if not dataset_path.is_file():
        msg = f"Dataset path does not exist or is not a file: {dataset_path}"
        raise FileNotFoundError(msg)
    return pd.read_csv(dataset_path)


def _check(
    checks: list[dict[str, object]],
    rule_id: str,
    status: str,
    severity: str,
    column: str,
    message: str,
    expected: object,
    observed: object,
) -> None:
    checks.append(
        {
            "rule_id": rule_id,
            "status": status,
            "severity": severity,
            "column": column,
            "message": message,
            "expected": expected,
            "observed": observed,
        }
    )


def _logical_type_compatible(series: pd.Series, logical_type: str) -> bool:
    non_null = series.dropna()
    if logical_type == "numeric":
        return bool(pd.api.types.is_numeric_dtype(series))
    if logical_type == "datetime":
        if non_null.empty:
            return True
        parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
        return bool(parsed.notna().all())
    if logical_type in {"categorical", "text"}:
        return True
    return True


def _validate_existing_column(
    df: pd.DataFrame,
    checks: list[dict[str, object]],
    column: str,
    column_contract: dict[str, object],
) -> None:
    series = df[column]
    logical_type = str(column_contract.get("logical_type", "unknown"))
    compatible = _logical_type_compatible(series, logical_type)
    _check(
        checks,
        f"type_compatible_{column}",
        "passed" if compatible else "failed",
        "warning",
        column,
        f"Column {column} is compatible with logical type {logical_type}.",
        logical_type,
        str(series.dtype),
    )

    missing_count = int(series.isna().sum())
    nullable = bool(column_contract.get("nullable", True))
    if not nullable:
        _check(
            checks,
            f"nullable_{column}",
            "passed" if missing_count == 0 else "failed",
            "warning",
            column,
            f"Column {column} has no missing values when nullable is false.",
            0,
            missing_count,
        )

    missing_percent = float(missing_count / len(df)) if len(df) else 0.0
    constraints = column_contract.get("constraints", {})
    assert isinstance(constraints, dict)
    if "max_missing_percent" in constraints:
        max_missing = float(constraints["max_missing_percent"])
        _check(
            checks,
            f"max_missing_percent_{column}",
            "passed" if missing_percent <= max_missing else "failed",
            "warning",
            column,
            f"Column {column} missing percent is within contract.",
            max_missing,
            missing_percent,
        )

    if logical_type == "numeric" and pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if "min_value" in constraints and not non_null.empty:
            observed_min = float(non_null.min())
            expected_min = float(constraints["min_value"])
            _check(
                checks,
                f"min_value_{column}",
                "passed" if observed_min >= expected_min else "failed",
                "warning",
                column,
                f"Column {column} minimum is within contract.",
                expected_min,
                observed_min,
            )
        if "max_value" in constraints and not non_null.empty:
            observed_max = float(non_null.max())
            expected_max = float(constraints["max_value"])
            _check(
                checks,
                f"max_value_{column}",
                "passed" if observed_max <= expected_max else "failed",
                "warning",
                column,
                f"Column {column} maximum is within contract.",
                expected_max,
                observed_max,
            )

    if "allowed_values" in constraints:
        allowed = {str(value) for value in constraints["allowed_values"]}
        observed = {str(value) for value in series.dropna().unique()}
        unknown = sorted(observed - allowed)
        _check(
            checks,
            f"allowed_values_{column}",
            "passed" if not unknown else "failed",
            "warning",
            column,
            f"Column {column} values are within allowed values.",
            sorted(allowed),
            unknown,
        )

    if bool(column_contract.get("uniqueness_hint", False)):
        unique_ratio = (
            float(series.nunique(dropna=True) / len(series)) if len(series) else 0.0
        )
        passed = unique_ratio >= 0.95
        _check(
            checks,
            f"uniqueness_hint_{column}",
            "passed" if passed else "failed",
            "warning",
            column,
            f"Column {column} satisfies high-uniqueness hint.",
            ">= 0.95",
            unique_ratio,
        )


def validate_dataset(
    dataset_path: str | Path,
    contract_path: str | Path,
) -> dict[str, object]:
    """Validate a dataset against a YAML data contract."""
    dataset = Path(dataset_path)
    contract_file = Path(contract_path)
    df = _load_dataset(dataset)
    contract = load_contract(contract_file)
    contract_columns = contract.get("columns", {})
    if not isinstance(contract_columns, dict):
        msg = "Contract 'columns' field must be a mapping."
        raise ValueError(msg)

    checks: list[dict[str, object]] = []
    for column, column_contract in contract_columns.items():
        assert isinstance(column_contract, dict)
        required = bool(column_contract.get("required", False))
        exists = column in df.columns
        _check(
            checks,
            f"column_required_{column}",
            "passed" if exists or not required else "failed",
            "critical",
            str(column),
            f"Required column {column} exists.",
            required,
            exists,
        )
        if exists:
            _validate_existing_column(df, checks, str(column), column_contract)

    failed_checks = sum(1 for check in checks if check["status"] == "failed")
    return {
        "passed": failed_checks == 0,
        "contract_path": contract_file.as_posix(),
        "dataset_path": dataset.as_posix(),
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - failed_checks,
            "failed_checks": failed_checks,
        },
        "checks": checks,
        "metadata": {
            "deterministic": True,
            "ai_generated": False,
        },
    }


def save_validation_result(result: dict, output_path: str | Path) -> Path:
    """Save validation result JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path
