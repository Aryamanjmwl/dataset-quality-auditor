
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from dqa.domain import AuditReport


@dataclass(frozen=True)
class JSONReporter:
    """
    Writes an AuditReport to a structured JSON file.
    """
    filename: str = "report.json"
    indent: int = 2

    def write(self, report: AuditReport, out_dir: Path) -> Path:
        out_dir = Path(out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / self.filename
        payload = report.to_dict()

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=self.indent, ensure_ascii=False)

        return out_path