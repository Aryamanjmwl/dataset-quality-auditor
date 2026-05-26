from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Union

from dqa.domain import (
    AuditContext,
    AuditReport,
    DatasetInfo,
    Finding,
    ScoreBreakdown,
    Severity,
)
from dqa.domain.interfaces import Check
from dqa.io import CSVDataLoader


@dataclass
class AuditRunner:
    checks: Sequence[Check]
    loader: CSVDataLoader

    def audit_csv(
        self,
        file_path: Union[str, Path],
        *,
        target: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> AuditReport:
        load_result = self.loader.load(file_path)
        df = load_result.df

        dataset_info = DatasetInfo(
            path=str(load_result.path),
            n_rows=load_result.n_rows,
            n_cols=load_result.n_cols,
            columns=list(df.columns),
        )

        ctx = AuditContext(target=target, params=params or {})

        findings: List[Finding] = []
        for check in self.checks:
            findings.extend(check.run(df, ctx))

        score = self._compute_score(findings, ctx)

        return AuditReport(
            dataset=dataset_info,
            findings=findings,
            health_score=score.final_score,
            score_breakdown=score,
        )

    @staticmethod
    def _compute_score(findings: List[Finding], ctx: AuditContext) -> ScoreBreakdown:
        """
        Severity-weighted scoring with caps to avoid a single dataset scoring 0 too easily.

        Tunable params (ctx.params):
        - score_weight_low (default 2)
        - score_weight_medium (default 6)
        - score_weight_high (default 12)
        - max_total_penalty (default 80)
        - max_penalty_per_finding_id (default 24)
        """
        w_low = float(ctx.params.get("score_weight_low", 2.0))
        w_med = float(ctx.params.get("score_weight_medium", 6.0))
        w_high = float(ctx.params.get("score_weight_high", 12.0))

        max_total_penalty = float(ctx.params.get("max_total_penalty", 80.0))
        max_penalty_per_id = float(ctx.params.get("max_penalty_per_finding_id", 24.0))

        weights = {
            Severity.LOW.value: w_low,
            Severity.MEDIUM.value: w_med,
            Severity.HIGH.value: w_high,
        }

        # Track penalty buckets by severity for explainability
        penalties = {k: 0.0 for k in weights.keys()}

        # Cap per finding id (e.g., OUTLIER_DETECTED could appear for many columns)
        per_id_accum: dict[str, float] = {}

        for f in findings:
            sev_key = f.severity.value
            p = weights.get(sev_key, 0.0)

            current = per_id_accum.get(f.id, 0.0)
            allowed = max(0.0, max_penalty_per_id - current)
            applied = min(p, allowed)

            per_id_accum[f.id] = current + applied
            penalties[sev_key] += applied

        base = 100.0
        total_penalty = min(max_total_penalty, sum(penalties.values()))
        final = max(0.0, min(100.0, base - total_penalty))

        # Note: penalties dict is still by severity; total penalty is capped globally.
        # If you want exact “after-cap” severity breakdown later, we can add it.
        return ScoreBreakdown(
            base_score=base,
            penalties=penalties,
            final_score=final,
        )
