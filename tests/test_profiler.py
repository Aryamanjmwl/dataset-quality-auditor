import pandas as pd

from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_profile_dataframe_returns_counts_and_column_metadata() -> None:
    df = pd.DataFrame(
        {
            "age": [18, 30, None, 30],
            "city": ["Berlin", "Paris", "Rome", "Madrid"],
            "label": [1, 0, 1, 0],
        }
    )
    df = pd.concat([df, df.iloc[[1]]], ignore_index=True)

    profile = profile_dataframe(df, target_column="label")

    assert profile["row_count"] == 5
    assert profile["column_count"] == 3
    assert profile["duplicate_row_count"] == 1
    assert profile["duplicate_row_percent"] == 0.2
    assert profile["columns"]["age"]["missing_count"] == 1
    assert profile["columns"]["age"]["is_numeric"] is True
    assert profile["columns"]["city"]["is_categorical"] is True
