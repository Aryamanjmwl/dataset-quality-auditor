import pandas as pd

from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_profiler_row_and_column_counts() -> None:
    df = pd.DataFrame(
        {
            "age": [18, 30, None],
            "city": ["Berlin", "Paris", "Berlin"],
            "label": [1, 0, 1],
        }
    )

    profile = profile_dataframe(df, target_column="label")

    assert profile["row_count"] == 3
    assert profile["column_count"] == 3
    assert profile["duplicate_row_count"] == 0
    assert profile["columns"]["age"]["missing_count"] == 1
    assert profile["columns"]["age"]["is_numeric"] is True
    assert profile["columns"]["city"]["categorical_summary"] is not None
