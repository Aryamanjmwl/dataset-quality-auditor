"""Structured deterministic issue model."""

from dataclasses import dataclass

from dataset_quality_auditor.audit.evidence import Evidence


@dataclass(frozen=True)
class Issue:
    issue_id: str
    check_id: str
    title: str
    severity: str
    risk_level: str
    status: str
    scope: dict[str, object]
    evidence: Evidence
    ml_impact: str
    recommendation: str
    requires_human_review: bool
    reproducibility: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "issue_id": self.issue_id,
            "check_id": self.check_id,
            "title": self.title,
            "severity": self.severity,
            "risk_level": self.risk_level,
            "status": self.status,
            "scope": self.scope,
            "evidence": self.evidence.to_dict(),
            "ml_impact": self.ml_impact,
            "recommendation": self.recommendation,
            "requires_human_review": self.requires_human_review,
            "reproducibility": self.reproducibility,
        }
