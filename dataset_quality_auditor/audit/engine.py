"""Deterministic audit engine."""

import json
from pathlib import Path

import pandas as pd

from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe
from dataset_quality_auditor.audit.registry import get_default_checks
from dataset_quality_auditor.audit.scoring import calculate_readiness_score

ENGINE_VERSION = "0.1.0"


def run_audit(
    dataset_path: str,
    target_column: str | None = None,
    output_dir: str = "reports",
) -> dict[str, object]:
    dataset = Path(dataset_path)
    if not dataset.is_file():
        msg = f"Dataset path does not exist or is not a file: {dataset_path}"
        raise FileNotFoundError(msg)
    df = pd.read_csv(dataset)
    if target_column is not None and target_column not in df.columns:
        msg = f"Target column '{target_column}' was not found in dataset."
        raise ValueError(msg)
    context = create_audit_context(
        dataset_path=dataset.as_posix(),
        target_column=target_column,
        output_dir=output_dir,
    )
    profile = profile_dataframe(df, target_column=target_column, config=context.config)
    issues = []
    for check in get_default_checks():
        issues.extend(check(df, profile, context))
    result = {
        "audit_id": context.audit_id,
        "created_at": context.created_at,
        "dataset_path": dataset.as_posix(),
        "target_column": target_column,
        "profile": profile,
        "issues": [issue.to_dict() for issue in issues],
        "score": calculate_readiness_score(issues),
        "metadata": {
            "package_version": context.package_version,
            "engine_version": ENGINE_VERSION,
            "deterministic": True,
            "ai_generated": False,
        },
    }
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "audit.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    return result
