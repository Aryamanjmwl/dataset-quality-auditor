"""Audit execution context."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from dataset_quality_auditor import __version__

DEFAULT_CONFIG: dict[str, float] = {
    "missing_warning_threshold": 0.10,
    "missing_critical_threshold": 0.40,
    "duplicate_warning_threshold": 0.01,
    "duplicate_critical_threshold": 0.10,
    "high_cardinality_threshold": 0.50,
    "imbalance_warning_threshold": 0.80,
    "id_unique_ratio_threshold": 0.95,
}


@dataclass(frozen=True)
class AuditContext:
    dataset_path: str
    target_column: str | None
    test_dataset_path: str | None
    output_dir: str
    audit_id: str
    created_at: str
    package_version: str
    config: dict[str, float] = field(default_factory=lambda: DEFAULT_CONFIG.copy())


def create_audit_context(
    dataset_path: str,
    target_column: str | None = None,
    test_dataset_path: str | None = None,
    output_dir: str = "reports",
    config: dict[str, float] | None = None,
) -> AuditContext:
    merged_config = DEFAULT_CONFIG.copy()
    if config:
        merged_config.update(config)
    return AuditContext(
        dataset_path=dataset_path,
        target_column=target_column,
        test_dataset_path=test_dataset_path,
        output_dir=output_dir,
        audit_id=str(uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        package_version=__version__,
        config=merged_config,
    )
