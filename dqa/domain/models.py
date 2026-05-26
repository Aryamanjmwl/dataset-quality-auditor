from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    """
    Severity level for a finding.

    Kept as str Enum so JSON serialization is clean (e.g. "HIGH").
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class DatasetInfo:
    """
    Basic metadata about the audited dataset.
    """

    path: str
    n_rows: int
    n_cols: int
    columns: List[str]


@dataclass(frozen=True)
class Finding:
    """
    One detected issue/risk in the dataset.
    """

    id: str
    title: str
    description: str
    severity: Severity
    columns: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendation: Optional[str] = None


@dataclass(frozen=True)
class ScoreBreakdown:
    """
    Explainable scoring breakdown.
    """

    base_score: float
    penalties: Dict[str, float]  # keys: "LOW","MEDIUM","HIGH"
    final_score: float


@dataclass(frozen=True)
class AuditReport:
    """
    Full output of an audit run.
    """

    dataset: DatasetInfo
    findings: List[Finding]
    health_score: float
    score_breakdown: ScoreBreakdown
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to a JSON-serializable dict.
        """
        return asdict(self)
