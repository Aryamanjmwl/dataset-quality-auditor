"""Column role inference."""

import re

import pandas as pd


def _unique_ratio(series: pd.Series) -> float:
    return float(series.nunique(dropna=True) / len(series)) if len(series) else 0.0


def _datetime_parse_ratio(series: pd.Series) -> float:
    non_null = series.dropna()
    if non_null.empty:
        return 0.0
    is_text = pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(
        series
    )
    if not is_text:
        return 0.0
    has_shape = non_null.astype(str).str.contains(re.compile(r"[-/:T]"), regex=True)
    if float(has_shape.mean()) < 0.80:
        return 0.0
    parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
    return float(parsed.notna().mean())


def infer_column_roles(
    df: pd.DataFrame,
    target_column: str | None = None,
    id_unique_ratio_threshold: float = 0.95,
) -> dict[str, str]:
    roles: dict[str, str] = {}
    for column in df.columns:
        if column == target_column:
            roles[column] = "target"
        elif _unique_ratio(df[column]) >= id_unique_ratio_threshold:
            roles[column] = "id_candidate"
        elif _datetime_parse_ratio(df[column]) >= 0.80:
            roles[column] = "datetime_candidate"
        else:
            roles[column] = "feature"
    return roles
