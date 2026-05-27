import pandas as pd

from dataset_quality_auditor.audit.checks.outliers import check_outlier_risk
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_iqr_outliers_create_issue() -> None:
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 100], "label": [0, 1] * 5})
    context = create_audit_context("data.csv", target_column="label")

    issues = check_outlier_risk(df, profile_dataframe(df, "label"), context)

    assert len(issues) == 1
    assert issues[0].check_id == "outlier_risk"
    assert issues[0].evidence.details["outlier_count"] == 1
