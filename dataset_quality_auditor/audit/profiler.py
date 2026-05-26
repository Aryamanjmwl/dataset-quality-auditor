"""Dataframe profiling for deterministic audits."""

from __future__ import annotations

import math

import pandas as pd

from dataset_quality_auditor.audit.context import DEFAULT_CONFIG
from dataset_quality_auditor.audit.schema import infer_column_roles


def _clean_number(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _numeric_summary(series: pd.Series) -> dict[str, float | None]:
    return {
        "min": _clean_number(series.min()),
        "max": _clean_number(series.max()),
        "mean": _clean_number(series.mean()),
        "std": _clean_number(series.std()),
    }


def _categorical_summary(series: pd.Series) -> dict[str, object]:
    top_values = [
        {"value": str(value), "count": int(count)}
        for value, count in series.value_counts(dropna=True).head(10).items()
    ]
    return {"top_values": top_values}


def profile_dataframe(
    df: pd.DataFrame,
    target_column: str | None = None,
    config: dict[str, float] | None = None,
) -> dict[str, object]:
    """Create a JSON-serializable profile for a dataframe."""
    audit_config = DEFAULT_CONFIG.copy()
    if config:
        audit_config.update(config)

    row_count = int(len(df))
    duplicate_row_count = int(df.duplicated().sum())
    duplicate_row_percent = (
        float(duplicate_row_count / row_count) if row_count > 0 else 0.0
    )
    roles = infer_column_roles(
        df,
        target_column=target_column,
        id_unique_ratio_threshold=audit_config["id_unique_ratio_threshold"],
    )

    columns: dict[str, object] = {}
    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))
        missing_percent = float(missing_count / row_count) if row_count > 0 else 0.0
        unique_percent = float(unique_count / row_count) if row_count > 0 else 0.0
        is_numeric = bool(pd.api.types.is_numeric_dtype(series))
        is_categorical = not is_numeric

        columns[column] = {
            "name": column,
            "dtype": str(series.dtype),
            "inferred_role": roles[column],
            "missing_count": missing_count,
            "missing_percent": missing_percent,
            "unique_count": unique_count,
            "unique_percent": unique_percent,
            "is_numeric": is_numeric,
            "is_categorical": is_categorical,
            "numeric_summary": _numeric_summary(series) if is_numeric else None,
            "categorical_summary": (
                _categorical_summary(series) if is_categorical else None
            ),
        }

    return {
        "row_count": row_count,
        "column_count": int(len(df.columns)),
        "target_column": target_column,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_row_percent": duplicate_row_percent,
        "columns": columns,
    }
