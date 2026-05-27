import pandas as pd

from dataset_quality_auditor.audit.checks.imbalance import check_class_imbalance
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_class_imbalance_detection() -> None:
    df = pd.DataFrame({"feature": range(10), "label": [1] * 9 + [0]})
    context = create_audit_context("data.csv", target_column="label")
    profile = profile_dataframe(df, target_column="label", config=context.config)

    issues = check_class_imbalance(df, profile, context)

    assert len(issues) == 1
    assert issues[0].evidence.details["dominant_class_ratio"] == 0.9
