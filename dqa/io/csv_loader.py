from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import pandas as pd


@dataclass(frozen=True)
class LoadResult:
    """
    Result of a dataset load operation.

    Attributes:
        df: Loaded dataset as a pandas DataFrame.
        path: Resolved path to the loaded file.
        n_rows: Number of rows.
        n_cols: Number of columns.
    """

    df: pd.DataFrame
    path: Path
    n_rows: int
    n_cols: int


class CSVDataLoader:
    """
    Production-oriented CSV loader.

    Why this exists:
    - Centralize CSV reading logic (encoding, separators, dtype inference decisions).
    - Provide a stable, testable contract for the rest of the system.
    - Add safety checks early (empty dataset, missing file, etc.).
    """

    def __init__(
        self,
        *,
        encoding: str = "utf-8",
        sep: str = ",",
        low_memory: bool = False,
        na_values: Optional[list[str]] = None,
    ) -> None:
        self.encoding = encoding
        self.sep = sep
        self.low_memory = low_memory
        self.na_values = na_values

    def load(self, file_path: Union[str, Path]) -> LoadResult:
        """
        Load a CSV file into a DataFrame.

        Args:
            file_path: Path to the CSV file.

        Returns:
            LoadResult containing the DataFrame and basic metadata.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the dataset is empty or unreadable.
        """
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Expected a .csv file, got: {path.name}")

        try:
            df = pd.read_csv(
                path,
                encoding=self.encoding,
                sep=self.sep,
                low_memory=self.low_memory,
                na_values=self.na_values,
            )
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {path} ({e})") from e

        if df.shape[0] == 0:
            raise ValueError(f"Dataset has 0 rows: {path}")
        if df.shape[1] == 0:
            raise ValueError(f"Dataset has 0 columns: {path}")

        # Normalize column names (common production annoyance)
        df.columns = [str(c).strip() for c in df.columns]

        return LoadResult(df=df, path=path, n_rows=df.shape[0], n_cols=df.shape[1])
