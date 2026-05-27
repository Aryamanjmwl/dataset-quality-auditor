"""JSON report helpers."""

import copy
import json
from pathlib import Path


def load_audit_json(path: str | Path) -> dict[str, object]:
    audit_path = Path(path)
    if not audit_path.is_file():
        msg = f"Audit JSON path does not exist or is not a file: {audit_path}"
        raise FileNotFoundError(msg)
    return json.loads(audit_path.read_text(encoding="utf-8"))


def save_json_report(audit_result: dict, output_path: str | Path) -> Path:
    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    preserved = copy.deepcopy(audit_result)
    report_path.write_text(json.dumps(preserved, indent=2), encoding="utf-8")
    return report_path
