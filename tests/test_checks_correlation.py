import pandas as pd

from dataset_quality_auditor.audit.checks.correlation import check_correlation_risk
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_highly_correlated_features_create_warning() -> None:
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 4, 6, 8], "label": [0, 0, 1, 1]})
    context = create_audit_context("data.csv", target_column="label")

    issues = check_correlation_risk(df, profile_dataframe(df, "label"), context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].evidence.details["correlation"] == 1.0
