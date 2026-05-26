import pandas as pd
from dqa.io import CSVDataLoader


def test_csv_loader_basic(tmp_path):
    # Create a temporary CSV file
    file_path = tmp_path / "test.csv"

    df = pd.DataFrame(
        {"age": [25, 30, 35], "income": [50000, 60000, 70000], "target": [0, 1, 0]}
    )

    df.to_csv(file_path, index=False)

    # Load using your loader
    loader = CSVDataLoader()
    result = loader.load(file_path)

    # Assertions
    assert result.df.shape == (3, 3)
    assert list(result.df.columns) == ["age", "income", "target"]
