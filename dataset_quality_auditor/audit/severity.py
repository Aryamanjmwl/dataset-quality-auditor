"""Severity and risk-level constants.

The audit model uses two related but separate axes:
- severity (critical/warning/info) drives deterministic score deductions.
- risk_level (high/medium/low) is metadata for display and filtering.
"""

CRITICAL = "critical"
WARNING = "warning"
INFO = "info"

HIGH = "high"
MEDIUM = "medium"
LOW = "low"
