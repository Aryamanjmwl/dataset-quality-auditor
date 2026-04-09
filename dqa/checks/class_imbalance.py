from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class ClassImbalanceCheck:
    """
    Detect class imbalance in a classification target column.
    """
    name: str = "class_imbalance"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        if not ctx.target:
            return []  # no target provided -> skip

        target = ctx.target
        if target not in df.columns:
            return [
                Finding(
                    id="TARGET_NOT_FOUND",
                    title="Target column not found",
                    description=f"Target column '{target}' was not found in the dataset.",
                    severity=Severity.HIGH,
                    columns=[target],
                    metrics={"provided_target": target},
                    recommendation="Pass the correct target column name (exact match) when running the audit.",
                )
            ]

        y = df[target].dropna()
        if y.empty:
            return [
                Finding(
                    id="TARGET_EMPTY",
                    title="Target column has no usable values",
                    description=f"Target column '{target}' contains only missing values.",
                    severity=Severity.HIGH,
                    columns=[target],
                    metrics={},
                    recommendation="Fix missing target values or remove empty rows before training.",
                )
            ]

        counts = y.value_counts(dropna=False)
        n = int(counts.sum())
        n_classes = int(counts.shape[0])

        # thresholds (configurable via ctx.params later)
        min_class_ratio_threshold = float(ctx.params.get("min_class_ratio_threshold", 0.10))  # 10%
        max_imbalance_ratio_threshold = float(ctx.params.get("max_imbalance_ratio_threshold", 5.0))  # max/min >= 5

        ratios = (counts / n).to_dict()

        min_ratio = float(min(ratios.values()))
        max_ratio = float(max(ratios.values()))

        # If binary/multi, compute max/min ratio safely
        min_count = int(counts.min())
        max_count = int(counts.max())
        max_min_ratio = (max_count / min_count) if min_count > 0 else float("inf")

        is_imbalanced = (min_ratio < min_class_ratio_threshold) or (max_min_ratio >= max_imbalance_ratio_threshold)

        if not is_imbalanced:
            return []

        # severity heuristic
        if min_ratio < 0.05 or max_min_ratio >= 10:
            sev = Severity.HIGH
        elif min_ratio < 0.10 or max_min_ratio >= 5:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        return [
            Finding(
                id="CLASS_IMBALANCE",
                title="Class imbalance detected",
                description=(
                    f"Target '{target}' is imbalanced across {n_classes} classes. "
                    f"Minority class ratio is {min_ratio:.2%}; max/min count ratio is {max_min_ratio:.2f}."
                ),
                severity=sev,
                columns=[target],
                metrics={
                    "n_samples": n,
                    "n_classes": n_classes,
                    "class_counts": {str(k): int(v) for k, v in counts.to_dict().items()},
                    "class_ratios": {str(k): round(float(v), 6) for k, v in ratios.items()},
                    "min_class_ratio": round(min_ratio, 6),
                    "max_min_count_ratio": round(float(max_min_ratio), 6),
                    "min_class_ratio_threshold": min_class_ratio_threshold,
                    "max_imbalance_ratio_threshold": max_imbalance_ratio_threshold,
                },
                recommendation=(
                    "Consider stratified train/test split, class weights, oversampling (e.g., SMOTE), "
                    "or collecting more minority-class samples. Also evaluate with F1/PR-AUC, not accuracy only."
                ),
            )
        ]