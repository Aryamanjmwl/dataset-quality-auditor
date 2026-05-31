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
    "numeric_drift_mean_shift_std_ratio": 1.0,
    "categorical_drift_dominant_category_shift": 0.30,
    "categorical_drift_missing_category_ratio": 0.50,
    "target_distribution_drift_warning_shift": 0.25,
    "target_distribution_drift_critical_shift": 0.50,
    "ks_drift_p_value_warning": 0.05,
    "ks_drift_p_value_info": 0.20,
}


@dataclass(frozen=True)
class AuditContext:
    """Runtime context shared by deterministic checks."""

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
    """Create an audit context with default thresholds."""
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
