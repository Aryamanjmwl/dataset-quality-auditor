from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dqa.domain import AuditReport


@dataclass(frozen=True)
class HTMLReporter:
    """
    Writes an AuditReport to an HTML file using a Jinja2 template.

    Adds computed summary fields:
    - severity_counts
    - top_findings (sorted by severity)
    """
    filename: str = "report.html"
    template_name: str = "report.html"

    def write(self, report: AuditReport, out_dir: Path) -> Path:
        out_dir = Path(out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        templates_dir = Path(__file__).parent / "templates"
        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        payload: Dict[str, Any] = report.to_dict()

        # Compute severity counts
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in payload.get("findings", []):
            sev = f.get("severity")
            if sev in counts:
                counts[sev] += 1

        # Compute top findings (sorted by severity rank)
        sev_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        findings_sorted: List[Dict[str, Any]] = sorted(
            payload.get("findings", []),
            key=lambda f: (sev_rank.get(f.get("severity", "LOW"), 1)),
            reverse=True,
        )

        payload["severity_counts"] = counts
        payload["top_findings"] = findings_sorted[:5]

        template = env.get_template(self.template_name)
        html = template.render(**payload)

        out_path = out_dir / self.filename
        out_path.write_text(html, encoding="utf-8")
        return out_path