"""Class imbalance checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import MEDIUM, WARNING


def check_class_imbalance(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    if not context.target_column or context.target_column not in df.columns:
        return []

    target = df[context.target_column].dropna()
    unique_count = int(target.nunique())
    if unique_count < 2 or unique_count > 20 or target.empty:
        return []

    distribution = target.value_counts(normalize=True).to_dict()
    class_distribution = {str(key): float(value) for key, value in distribution.items()}
    dominant_class_ratio = max(class_distribution.values())
    if dominant_class_ratio < context.config["imbalance_warning_threshold"]:
        return []

    return [
        Issue(
            issue_id=issue_id("class_imbalance", context.target_column),
            check_id="class_imbalance",
            title="Target class imbalance detected",
            severity=WARNING,
            risk_level=MEDIUM,
            status="failed",
            scope={
                "dataset": "train",
                "column": context.target_column,
                "column_role": "target",
            },
            evidence=Evidence(
                metric="dominant_class_ratio",
                observed_value=dominant_class_ratio,
                threshold=context.config["imbalance_warning_threshold"],
                comparison="observed_value >= threshold",
                details={
                    "class_distribution": class_distribution,
                    "dominant_class_ratio": dominant_class_ratio,
                    "total_rows": int(profile["row_count"]),
                },
            ),
            ml_impact=(
                "Imbalanced classes can produce misleading accuracy and weak "
                "minority-class performance."
            ),
            recommendation=(
                "Use stratified validation and consider class-aware metrics, "
                "sampling, or weighting in the training pipeline."
            ),
            requires_human_review=False,
            reproducibility=reproducibility(
                context,
                {
                    "imbalance_warning_threshold": context.config[
                        "imbalance_warning_threshold"
                    ]
                },
            ),
        )
    ]
