import pandas as pd

from dataset_quality_auditor.audit.schema import infer_column_roles


def test_schema_infers_target_id_and_datetime_candidates() -> None:
    df = pd.DataFrame(
        {
            "record_key": ["a", "b", "c", "d"],
            "event_date": ["2026-01-01", "2026-01-02", "2026-01-03", None],
            "feature": ["x", "x", "y", "y"],
            "label": [0, 1, 0, 1],
        }
    )

    roles = infer_column_roles(
        df,
        target_column="label",
        id_unique_ratio_threshold=1.0,
    )

    assert roles["label"] == "target"
    assert roles["record_key"] == "id_candidate"
    assert roles["event_date"] == "datetime_candidate"
    assert roles["feature"] == "feature"
