"""Recommendation text used by deterministic checks."""

MISSING_VALUES = (
    "Handle missing values inside the preprocessing pipeline fitted only on "
    "training data."
)

HIGH_CARDINALITY = (
    "Confirm whether this column is an identifier or a usable model feature "
    "before training."
)

ID_LIKE = (
    "Confirm whether this column is an ID and whether it is available at "
    "prediction time."
)

DATATYPE_RISK = (
    "Add explicit schema and type validation before model training."
)
