"""Schema helpers for deterministic data contracts."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

CONTRACT_VERSION = "0.1.0"
CREATED_BY = "dataset-quality-auditor"


def yaml_safe_value(value: object) -> object:
    """Convert pandas/numpy values into YAML-safe Python values."""
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def sorted_string_values(values: Iterable[object]) -> list[str]:
    """Return deterministic string values for categorical metadata."""
    return sorted(str(yaml_safe_value(value)) for value in values)


def base_contract(
    dataset_path: str,
    target_column: str | None,
    row_count: int,
    column_count: int,
) -> dict[str, object]:
    """Create the top-level contract dictionary."""
    return {
        "contract_version": CONTRACT_VERSION,
        "created_by": CREATED_BY,
        "dataset": {
            "source": dataset_path,
            "target_column": target_column,
            "row_count_observed": row_count,
            "column_count_observed": column_count,
        },
        "columns": {},
        "target": None,
        "metadata": {
            "deterministic": True,
            "ai_generated": False,
        },
    }
