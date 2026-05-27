import pandas as pd

from dataset_quality_auditor.audit.checks.overlap import check_train_test_overlap
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_overlapping_rows_produce_critical_issue() -> None:
    train = pd.DataFrame({"age": [1, 2], "label": [0, 1]})
    test = pd.DataFrame({"age": [2, 3], "label": [1, 0]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_overlap(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert len(issues) == 1
    assert issues[0].severity == "critical"
    assert issues[0].evidence.details["overlapping_row_count"] == 1
