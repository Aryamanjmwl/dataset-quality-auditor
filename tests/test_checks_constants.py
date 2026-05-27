import pandas as pd

from dataset_quality_auditor.audit.checks.constants import check_constant_columns
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe
from dataset_quality_auditor.audit.severity import CRITICAL, WARNING


def test_constant_feature_and_target() -> None:
    df = pd.DataFrame({"constant": ["x", "x", "x"], "label": [1, 1, 1]})
    context = create_audit_context("data.csv", target_column="label")
    profile = profile_dataframe(df, target_column="label", config=context.config)

    issues = check_constant_columns(df, profile, context)
    severities = {issue.scope["column"]: issue.severity for issue in issues}

    assert severities["constant"] == WARNING
    assert severities["label"] == CRITICAL
