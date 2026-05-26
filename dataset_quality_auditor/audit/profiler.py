"""Dataframe profiler."""

import math

import pandas as pd

from dataset_quality_auditor.audit.context import DEFAULT_CONFIG
from dataset_quality_auditor.audit.schema import infer_column_roles


def _clean_number(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return None if math.isnan(number) or math.isinf(number) else number


def profile_dataframe(
    df: pd.DataFrame,
    target_column: str | None = None,
    config: dict[str, float] | None = None,
) -> dict[str, object]:
    audit_config = DEFAULT_CONFIG.copy()
    if config:
        audit_config.update(config)
    row_count = int(len(df))
    duplicate_row_count = int(df.duplicated().sum())
    roles = infer_column_roles(
        df, target_column, audit_config["id_unique_ratio_threshold"]
    )
    columns: dict[str, object] = {}
    for column in df.columns:
        series = df[column]
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))
        is_numeric = bool(pd.api.types.is_numeric_dtype(series))
        numeric_summary = None
        if is_numeric:
            numeric_summary = {
                "min": _clean_number(series.min()),
                "max": _clean_number(series.max()),
                "mean": _clean_number(series.mean()),
                "std": _clean_number(series.std()),
            }
        categorical_summary = None
        if not is_numeric:
            categorical_summary = {
                "top_values": [
                    {"value": str(value), "count": int(count)}
                    for value, count in series.value_counts(dropna=True)
                    .head(10)
                    .items()
                ]
            }
        columns[column] = {
            "name": column,
            "dtype": str(series.dtype),
            "inferred_role": roles[column],
            "missing_count": missing_count,
            "missing_percent": float(missing_count / row_count) if row_count else 0.0,
            "unique_count": unique_count,
            "unique_percent": float(unique_count / row_count) if row_count else 0.0,
            "is_numeric": is_numeric,
            "is_categorical": not is_numeric,
            "numeric_summary": numeric_summary,
            "categorical_summary": categorical_summary,
        }
    return {
        "row_count": row_count,
        "column_count": int(len(df.columns)),
        "target_column": target_column,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_row_percent": (
            float(duplicate_row_count / row_count) if row_count else 0.0
        ),
        "columns": columns,
    }
