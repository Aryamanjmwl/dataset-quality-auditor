"""Generate deterministic synthetic train/test CSVs for demos."""

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
OUTPUT_DIR = Path(__file__).parent


def _target(n: int, positive_rate: float) -> np.ndarray:
    return RNG.binomial(1, positive_rate, n)


def _post_event_score(target: np.ndarray) -> np.ndarray:
    noise = RNG.normal(0, 0.05, len(target))
    return np.clip(target + noise, 0, 1)


def make_train() -> pd.DataFrame:
    n = 2_000
    target = _target(n, 0.20)
    missing_feature = RNG.normal(10, 2, n)
    missing_feature[RNG.random(n) < 0.25] = np.nan
    return pd.DataFrame(
        {
            "age": np.clip(20 + RNG.gamma(4, 6, n), 20, 65).astype(int),
            "income": np.clip(RNG.normal(50_000, 15_000, n), 1, None),
            "credit_score": np.clip(RNG.normal(650, 100, n), 300, 850).astype(int),
            "loan_amount": RNG.uniform(5_000, 50_000, n),
            "employment_years": np.clip(RNG.exponential(6, n), 0, 30),
            "region": RNG.choice(["north", "south", "east", "west"], n),
            "product_type": RNG.choice(["A", "B", "C"], n, p=[0.70, 0.20, 0.10]),
            "missing_feature": missing_feature,
            "duplicate_prone": RNG.integers(1, 6, n),
            "id_col": np.arange(1, n + 1),
            "target": target,
            "post_event_score": _post_event_score(target),
        }
    )


def make_test() -> pd.DataFrame:
    n = 500
    target = _target(n, 0.20)
    missing_feature = RNG.normal(10, 2, n)
    missing_feature[RNG.random(n) < 0.35] = np.nan
    return pd.DataFrame(
        {
            "age": np.clip(28 + RNG.gamma(4, 6, n), 20, 75).astype(int),
            "income": np.clip(RNG.normal(50_000, 15_000, n), 1, None),
            "credit_score": np.clip(RNG.normal(650, 100, n), 300, 850).astype(int),
            "loan_amount": RNG.uniform(5_000, 50_000, n),
            "employment_years": np.clip(RNG.exponential(6, n), 0, 30),
            "region": RNG.choice(["north", "south", "east", "west", "central"], n),
            "product_type": RNG.choice(["A", "B", "C"], n, p=[0.40, 0.40, 0.20]),
            "missing_feature": missing_feature,
            "duplicate_prone": RNG.integers(1, 6, n),
            "id_col": np.arange(10_001, 10_001 + n),
            "target": target,
            "post_event_score": _post_event_score(target),
        }
    )


def main() -> None:
    make_train().to_csv(OUTPUT_DIR / "synthetic_train.csv", index=False)
    make_test().to_csv(OUTPUT_DIR / "synthetic_test.csv", index=False)


if __name__ == "__main__":
    main()
