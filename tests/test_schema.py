import pandas as pd

from dataset_quality_auditor.audit.schema import infer_column_roles


def test_schema_role_inference() -> None:
    df = pd.DataFrame(
        {
            "record_id": ["a", "b", "c", "d"],
            "event_date": ["2025-01-01", "2025-01-02", "2025-01-03", None],
            "feature": ["x", "x", "y", "z"],
            "label": [0, 1, 0, 1],
        }
    )

    roles = infer_column_roles(df, target_column="label", id_unique_ratio_threshold=1.0)

    assert roles["label"] == "target"
    assert roles["record_id"] == "id_candidate"
    assert roles["event_date"] == "datetime_candidate"
    assert roles["feature"] == "feature"
