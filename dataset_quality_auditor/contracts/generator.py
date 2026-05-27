"""Deterministic data contract generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from dataset_quality_auditor.audit.context import DEFAULT_CONFIG
from dataset_quality_auditor.audit.profiler import profile_dataframe
from dataset_quality_auditor.contracts.schema import (
    base_contract,
    sorted_string_values,
    yaml_safe_value,
)

LOW_CARDINALITY_LIMIT = 50
MISSING_TOLERANCE = 0.05


def _load_dataset(dataset_path: str | Path) -> pd.DataFrame:
    path = Path(dataset_path)
    if not path.is_file():
        msg = f"Dataset path does not exist or is not a file: {path}"
        raise FileNotFoundError(msg)
    return pd.read_csv(path)


def _logical_type(series: pd.Series, column_profile: dict[str, object]) -> str:
    role = str(column_profile["inferred_role"])
    if role == "datetime_candidate":
        return "datetime"
    if bool(column_profile["is_numeric"]):
        return "numeric"
    unique_count = int(column_profile["unique_count"])
    if unique_count <= LOW_CARDINALITY_LIMIT:
        return "categorical"
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        return "text"
    return "unknown"


def _numeric_contract(column_profile: dict[str, object]) -> dict[str, object] | None:
    summary = column_profile.get("numeric_summary")
    if not isinstance(summary, dict):
        return None
    return {
        "min_observed": yaml_safe_value(summary.get("min")),
        "max_observed": yaml_safe_value(summary.get("max")),
    }


def _categorical_contract(
    series: pd.Series,
    logical_type: str,
) -> dict[str, object] | None:
    values = series.dropna().unique()
    if logical_type != "categorical" or len(values) > LOW_CARDINALITY_LIMIT:
        return None
    return {"allowed_values_observed": sorted_string_values(values)}


def _column_contract(
    df: pd.DataFrame,
    column: str,
    column_profile: dict[str, object],
) -> dict[str, object]:
    series = df[column]
    logical_type = _logical_type(series, column_profile)
    missing_percent = float(column_profile["missing_percent"])
    numeric = _numeric_contract(column_profile) if logical_type == "numeric" else None
    categorical = _categorical_contract(series, logical_type)
    constraints: dict[str, object] = {
        "max_missing_percent": min(1.0, missing_percent + MISSING_TOLERANCE),
    }
    if numeric:
        constraints["min_value"] = numeric["min_observed"]
        constraints["max_value"] = numeric["max_observed"]
    if categorical:
        constraints["allowed_values"] = categorical["allowed_values_observed"]

    role = str(column_profile["inferred_role"])
    contract: dict[str, object] = {
        "required": True,
        "role": role,
        "logical_type": logical_type,
        "pandas_dtype_observed": str(column_profile["dtype"]),
        "nullable": bool(missing_percent > 0),
        "missing_percent_observed": missing_percent,
        "unique_percent_observed": float(column_profile["unique_percent"]),
        "numeric": numeric,
        "categorical": categorical,
        "constraints": constraints,
    }
    if role == "id_candidate":
        contract["uniqueness_hint"] = True
        contract["requires_human_review"] = True
    return contract


def _target_metadata(
    df: pd.DataFrame,
    target_column: str | None,
) -> dict[str, object] | None:
    if target_column is None or target_column not in df.columns:
        return None
    target = df[target_column].dropna()
    return {
        "name": target_column,
        "logical_type": "categorical"
        if int(target.nunique()) <= LOW_CARDINALITY_LIMIT
        else "unknown",
        "classes_observed": sorted_string_values(target.unique()),
        "class_distribution_observed": {
            str(key): int(value)
            for key, value in target.value_counts().sort_index().items()
        },
    }


def generate_contract(
    dataset_path: str | Path,
    target_column: str | None = None,
) -> dict[str, object]:
    """Generate a deterministic YAML-serializable data contract."""
    path = Path(dataset_path)
    df = _load_dataset(path)
    if target_column is not None and target_column not in df.columns:
        msg = f"Target column '{target_column}' was not found in dataset."
        raise ValueError(msg)

    profile = profile_dataframe(df, target_column=target_column, config=DEFAULT_CONFIG)
    contract = base_contract(
        dataset_path=path.as_posix(),
        target_column=target_column,
        row_count=int(profile["row_count"]),
        column_count=int(profile["column_count"]),
    )
    columns = profile["columns"]
    assert isinstance(columns, dict)
    contract_columns: dict[str, object] = {}
    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        contract_columns[str(column)] = _column_contract(
            df,
            str(column),
            column_profile,
        )
    contract["columns"] = contract_columns
    contract["target"] = _target_metadata(df, target_column)
    return contract


def save_contract(contract: dict, output_path: str | Path) -> Path:
    """Save a data contract as YAML."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(contract, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path
