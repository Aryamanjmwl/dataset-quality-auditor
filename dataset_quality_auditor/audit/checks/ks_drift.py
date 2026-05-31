"""Optional Kolmogorov-Smirnov train/test drift check."""

import warnings

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import INFO, LOW, MEDIUM, WARNING


def check_ks_drift(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Run a two-sample KS test for shared numeric train/test features."""
    try:
        from scipy.stats import ks_2samp
    except ImportError:
        warnings.warn(
            "scipy is not installed; ks_drift check skipped. "
            "Install with: pip install scipy",
            UserWarning,
            stacklevel=2,
        )
        return []

    warning_threshold = context.config["ks_drift_p_value_warning"]
    info_threshold = context.config["ks_drift_p_value_info"]
    issues: list[Issue] = []
    shared = set(train_df.columns) & set(test_df.columns)
    for column in sorted(shared):
        if column == context.target_column:
            continue
        if not (
            pd.api.types.is_numeric_dtype(train_df[column])
            and pd.api.types.is_numeric_dtype(test_df[column])
        ):
            continue
        train_values = train_df[column].dropna()
        test_values = test_df[column].dropna()
        if train_values.empty or test_values.empty:
            continue

        result = ks_2samp(train_values, test_values)
        p_value = float(result.pvalue)
        if p_value < warning_threshold:
            severity, risk, threshold = WARNING, MEDIUM, warning_threshold
        elif p_value < info_threshold:
            severity, risk, threshold = INFO, LOW, info_threshold
        else:
            continue

        issues.append(
            Issue(
                issue_id=issue_id("ks_drift", column),
                check_id="ks_drift",
                title="KS-test train/test drift detected",
                severity=severity,
                risk_level=risk,
                status="failed",
                scope={
                    "dataset": "train_test",
                    "column": column,
                    "column_role": "feature",
                },
                evidence=Evidence(
                    metric="ks_p_value",
                    observed_value=p_value,
                    threshold=threshold,
                    comparison="observed_value < threshold",
                    details={
                        "ks_statistic": float(result.statistic),
                        "p_value": p_value,
                        "train_n": int(len(train_values)),
                        "test_n": int(len(test_values)),
                    },
                ),
                ml_impact=(
                    "Statistically significant distribution shift may cause "
                    "train/test metric gap."
                ),
                recommendation=(
                    "KS test suggests distributional difference "
                    f"(p={p_value:.4f}); inspect feature distributions before "
                    "training."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(
                    context,
                    {
                        "p_value_warning": warning_threshold,
                        "p_value_info": info_threshold,
                    },
                ),
            )
        )
    return issues
