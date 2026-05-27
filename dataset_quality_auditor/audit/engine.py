"""Deterministic audit engine."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe
from dataset_quality_auditor.audit.registry import (
    get_default_checks,
    get_train_test_checks,
)
from dataset_quality_auditor.audit.scoring import calculate_readiness_score

ENGINE_VERSION = "0.1.0"


def run_audit(
    dataset_path: str,
    target_column: str | None = None,
    test_dataset_path: str | None = None,
    output_dir: str = "reports",
) -> dict[str, object]:
    """Run a deterministic audit for a CSV dataset and write audit.json."""
    dataset = Path(dataset_path)
    if not dataset.is_file():
        msg = f"Dataset path does not exist or is not a file: {dataset_path}"
        raise FileNotFoundError(msg)

    train_df = pd.read_csv(dataset)
    if target_column is not None and target_column not in train_df.columns:
        msg = f"Target column '{target_column}' was not found in dataset."
        raise ValueError(msg)

    test_dataset = Path(test_dataset_path) if test_dataset_path is not None else None
    test_df: pd.DataFrame | None = None
    if test_dataset is not None:
        if not test_dataset.is_file():
            msg = (
                "Test dataset path does not exist or is not a file: "
                f"{test_dataset_path}"
            )
            raise FileNotFoundError(msg)
        test_df = pd.read_csv(test_dataset)

    context = create_audit_context(
        dataset_path=dataset.as_posix(),
        target_column=target_column,
        test_dataset_path=test_dataset.as_posix() if test_dataset else None,
        output_dir=output_dir,
    )
    train_profile = profile_dataframe(
        train_df,
        target_column=target_column,
        config=context.config,
    )

    issues = []
    for check in get_default_checks():
        issues.extend(check(train_df, train_profile, context))

    mode = "single_dataset"
    profile: dict[str, object] = train_profile
    if test_df is not None:
        mode = "train_test"
        test_profile = profile_dataframe(
            test_df,
            target_column=target_column if target_column in test_df.columns else None,
            config=context.config,
        )
        for check in get_train_test_checks():
            issues.extend(
                check(train_df, test_df, train_profile, test_profile, context)
            )
        profile = {"train": train_profile, "test": test_profile}

    score = calculate_readiness_score(issues)
    result = {
        "audit_id": context.audit_id,
        "created_at": context.created_at,
        "mode": mode,
        "dataset_path": dataset.as_posix(),
        "test_dataset_path": test_dataset.as_posix() if test_dataset else None,
        "target_column": target_column,
        "profile": profile,
        "issues": [issue.to_dict() for issue in issues],
        "score": score,
        "metadata": {
            "package_version": context.package_version,
            "engine_version": ENGINE_VERSION,
            "deterministic": True,
            "ai_generated": False,
        },
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    audit_json_path = output_path / "audit.json"
    audit_json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result
