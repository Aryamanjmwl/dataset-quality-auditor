import tempfile
from pathlib import Path

import pandas as pd

from dqa.io import CSVDataLoader


def test_csv_loader_basic(tmp_path):
    data = tmp_path / "sample.csv"
    data.write_text("a,b\n1,2\n3,4\n")
    loader = CSVDataLoader()
    result = loader.load(data)
    assert result.n_rows == 2
    assert result.n_cols == 2
    assert list(result.df.columns) == ["a", "b"]
