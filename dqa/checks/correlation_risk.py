from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class CorrelationRiskCheck:
    """
    Detect highly correlated numeric feature pairs.

    High correlation can cause:
    - multicollinearity (unstable coefficients in linear/logistic regression)
    - redundant features
    - leakage-like behavior if a derived feature encodes target or future info
    """
    name: str = "correlation_risk"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        threshold = float(ctx.params.get("correlation_threshold", 0.90))

        # Select numeric columns only (exclude target if numeric)
        num_df = df.select_dtypes(include=[np.number]).copy()
        if ctx.target and ctx.target in num_df.columns:
            num_df = num_df.drop(columns=[ctx.target])

        if num_df.shape[1] < 2:
            return []

        corr = num_df.corr(numeric_only=True).abs()

        # Upper triangle pairs
        pairs: List[Tuple[str, str, float]] = []
        cols = list(corr.columns)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = float(corr.iloc[i, j])
                if val >= threshold and not np.isnan(val):
                    pairs.append((cols[i], cols[j], val))

        if not pairs:
            return []

        # Sort most severe correlations first
        pairs.sort(key=lambda x: x[2], reverse=True)

        # Severity heuristic based on top correlation
        top_corr = pairs[0][2]
        if top_corr >= 0.98:
            sev = Severity.HIGH
        elif top_corr >= 0.95:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        # Keep report readable: show top N
        top_n = int(ctx.params.get("correlation_top_n", 10))
        shown = pairs[:top_n]

        return [
            Finding(
                id="FEATURE_CORRELATION_RISK",
                title="Highly correlated numeric features detected",
                description=(
                    f"Found {len(pairs)} highly correlated feature pair(s) with |corr| >= {threshold}. "
                    "Highly correlated features may be redundant and can destabilize linear models."
                ),
                severity=sev,
                columns=sorted(list({c for a, b, _ in pairs for c in (a, b)})),
                metrics={
                    "threshold": threshold,
                    "num_numeric_features_checked": int(num_df.shape[1]),
                    "num_pairs_flagged": int(len(pairs)),
                    "top_pairs": [
                        {"feature_1": a, "feature_2": b, "abs_corr": round(v, 6)}
                        for a, b, v in shown
                    ],
                },
                recommendation=(
                    "Consider removing one feature from each highly correlated pair, or use regularization "
                    "(Ridge/Lasso), PCA, or tree-based models. Also check if any feature is a target proxy "
                    "or derived from future information (leakage risk)."
                ),
            )
        ]