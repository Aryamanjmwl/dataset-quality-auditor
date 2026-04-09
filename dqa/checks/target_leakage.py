from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class TargetLeakageCheck:
    """
    Detect potential target leakage.

    Aggregated behavior:
    - One finding for correlated features (TARGET_LEAKAGE_CORRELATION) listing all suspicious columns
    - One finding for proxy/identical features (TARGET_LEAKAGE_PROXY) listing all identical columns
    """
    name: str = "target_leakage"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        if not ctx.target or ctx.target not in df.columns:
            return []

        threshold = float(ctx.params.get("leakage_corr_threshold", 0.95))

        # Only numeric features for correlation
        num_df = df.select_dtypes(include=[np.number]).copy()
        if ctx.target not in num_df.columns:
            return []

        y = num_df[ctx.target]
        corr_hits: Dict[str, float] = {}
        proxy_cols: List[str] = []

        for col in num_df.columns:
            if col == ctx.target:
                continue

            aligned = pd.concat([num_df[col], y], axis=1).dropna()
            if aligned.empty:
                continue

            corr = float(abs(aligned[col].corr(aligned[ctx.target])))

            if corr >= threshold:
                corr_hits[col] = round(corr, 6)

            if aligned[col].equals(aligned[ctx.target]):
                proxy_cols.append(col)

        findings: List[Finding] = []

        if corr_hits:
            max_corr = max(corr_hits.values())
            sev = Severity.HIGH if max_corr >= 0.98 else Severity.MEDIUM

            findings.append(
                Finding(
                    id="TARGET_LEAKAGE_CORRELATION",
                    title="Features highly correlated with target (possible leakage)",
                    description=(
                        f"{len(corr_hits)} numeric feature(s) have |corr| >= {threshold} with target "
                        f"'{ctx.target}'. This may indicate leakage (target proxy or future info)."
                    ),
                    severity=sev,
                    columns=sorted(list(corr_hits.keys())) + [ctx.target],
                    metrics={
                        "threshold": threshold,
                        "abs_correlations": corr_hits,
                        "max_abs_correlation": max_corr,
                    },
                    recommendation=(
                        "Inspect these features carefully. If they are derived from the label, computed "
                        "post-event, or include future information, remove them or redesign the feature."
                    ),
                )
            )

        if proxy_cols:
            findings.append(
                Finding(
                    id="TARGET_LEAKAGE_PROXY",
                    title="Feature(s) identical to target (direct leakage)",
                    description=(
                        f"{len(proxy_cols)} feature(s) are identical to the target column '{ctx.target}'."
                    ),
                    severity=Severity.HIGH,
                    columns=sorted(proxy_cols) + [ctx.target],
                    metrics={"proxy_columns": sorted(proxy_cols)},
                    recommendation="Remove these feature(s) immediately. They directly leak the target.",
                )
            )

        return findings