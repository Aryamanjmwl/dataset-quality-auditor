"""Evidence model for deterministic audit issues."""

from dataclasses import dataclass, field

ObservedValue = int | float | str | bool


@dataclass(frozen=True)
class Evidence:
    metric: str
    observed_value: ObservedValue
    threshold: ObservedValue | None
    comparison: str
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "comparison": self.comparison,
            "details": self.details,
        }
