"""Default deterministic check registry."""

from collections.abc import Callable

import pandas as pd

from dataset_quality_auditor.audit.checks.cardinality import check_high_cardinality
from dataset_quality_auditor.audit.checks.constants import check_constant_columns
from dataset_quality_auditor.audit.checks.datatypes import check_datatype_risks
from dataset_quality_auditor.audit.checks.duplicates import check_duplicate_rows
from dataset_quality_auditor.audit.checks.id_like import check_id_like_columns
from dataset_quality_auditor.audit.checks.imbalance import check_class_imbalance
from dataset_quality_auditor.audit.checks.missing import check_missing_values
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.issues import Issue

Check = Callable[[pd.DataFrame, dict[str, object], AuditContext], list[Issue]]


def get_default_checks() -> list[Check]:
    """Return checks run by the Phase 2 audit engine."""
    return [
        check_missing_values,
        check_duplicate_rows,
        check_constant_columns,
        check_high_cardinality,
        check_class_imbalance,
        check_id_like_columns,
        check_datatype_risks,
    ]
