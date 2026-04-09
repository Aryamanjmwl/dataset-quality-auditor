"""Utility script for printing findings from a JSON report file."""

import json
from pathlib import Path
import sys


def main(report_path: str = "reports/report.json") -> int:
    path = Path(report_path)
    if not path.exists():
        print(f"Report not found: {path}", file=sys.stderr)
        return 1

    try:
        r = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read JSON report: {e}", file=sys.stderr)
        return 1

    findings = r.get("findings", [])
    print(f"Total findings: {len(findings)}")
    for f in findings:
        print(f"{f.get('id')} {f.get('severity')}")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="print_findings", description="Print findings from a report JSON file")
    parser.add_argument("--report", default="reports/report.json", help="Path to report JSON file")
    args = parser.parse_args()
    sys.exit(main(args.report))
