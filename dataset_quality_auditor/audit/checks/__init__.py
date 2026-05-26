"""Deterministic audit checks."""

import re

from dataset_quality_auditor.audit.context import AuditContext


def issue_id(check_id: str, subject: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", subject.lower()).strip("_")
    return f"{check_id}_{normalized}_001"


def reproducibility(
    context: AuditContext,
    parameters: dict[str, object],
) -> dict[str, object]:
    return {"check_version": context.package_version, "parameters": parameters}
