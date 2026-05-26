from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Protocol, runtime_checkable

import pandas as pd

from dqa.domain.models import Finding


@dataclass(frozen=True)
class AuditContext:
    """
    Context/config passed to checks.

    This avoids hardcoding things like target column name inside each check.
    """

    target: Optional[str] = None
    # You can store additional runtime config here as you grow:
    params: Dict[str, object] = field(default_factory=dict)


@runtime_checkable
class Check(Protocol):
    """
    A dataset check that returns a list of findings.
    """

    name: str

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]: ...


@runtime_checkable
class Reporter(Protocol):
    """
    A reporter writes an AuditReport somewhere (json/html/etc).
    """

    def write(self, report: object, out_dir: Path) -> Path: ...
