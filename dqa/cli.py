from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from dqa.application import AuditRunner
from dqa.checks import (
    ClassImbalanceCheck,
    CorrelationRiskCheck,
    DataDriftCheck,
    HighCardinalityCategoricalCheck,
    MissingValuesCheck,
    OutlierDetectionCheck,
    TargetLeakageCheck,
    TrainTestOverlapCheck,
)
from dqa.config import Config, merge_params
from dqa.io import CSVDataLoader
from dqa.reporting import HTMLReporter, JSONReporter


def _build_runner() -> AuditRunner:
    return AuditRunner(
        checks=[
            MissingValuesCheck(),
            ClassImbalanceCheck(),
            HighCardinalityCategoricalCheck(),
            CorrelationRiskCheck(),
            OutlierDetectionCheck(),
            TrainTestOverlapCheck(),
            TargetLeakageCheck(),
            DataDriftCheck(),
        ],
        loader=CSVDataLoader(),
    )


def _parse_kv_list(items: Optional[List[str]]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if not items:
        return params

    for it in items:
        if "=" not in it:
            raise ValueError(f"Invalid --param '{it}'. Use key=value.")
        k, v = it.split("=", 1)
        v_strip = v.strip()

        if v_strip.lower() in {"true", "false"}:
            params[k] = v_strip.lower() == "true"
        else:
            try:
                if "." in v_strip:
                    params[k] = float(v_strip)
                else:
                    params[k] = int(v_strip)
            except ValueError:
                params[k] = v_strip

    return params


def main() -> None:
    parser = argparse.ArgumentParser(prog="dqa", description="Dataset Quality Auditor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    audit = sub.add_parser("audit", help="Audit a CSV dataset and generate reports.")
    audit.add_argument("--data", required=True, help="Path to CSV dataset.")
    audit.add_argument("--target", default=None, help="Target column name (optional).")
    audit.add_argument("--out", default="reports", help="Output directory for reports.")

    audit.add_argument(
        "--train", default=None, help="Optional train CSV path (overlap check)."
    )
    audit.add_argument(
        "--test", default=None, help="Optional test CSV path (overlap check)."
    )

    audit.add_argument("--ref", default=None, help="Reference CSV path (drift check).")
    audit.add_argument("--cur", default=None, help="Current CSV path (drift check).")

    audit.add_argument(
        "--config", default=None, help="Path to config .yaml/.yml or .json"
    )
    audit.add_argument(
        "--param",
        action="append",
        default=[],
        help="Extra params key=value (repeatable).",
    )

    audit.add_argument("--debug", action="store_true", help="Print debug info")
    audit.add_argument(
        "--print-findings", action="store_true", help="Print finding IDs + severity"
    )

    args = parser.parse_args()

    config_params: Dict[str, Any] = {}
    if args.config:
        config_params = Config.load(args.config).params

    cli_params = _parse_kv_list(args.param)
    params = merge_params(config_params, cli_params)

    if args.train and args.test:
        params["train_path"] = args.train
        params["test_path"] = args.test

    if args.ref and args.cur:
        params["reference_path"] = args.ref
        params["current_path"] = args.cur

    if args.debug:
        print("DEBUG: runner params =", params)

    runner = _build_runner()
    report = runner.audit_csv(args.data, target=args.target, params=params)

    if args.debug or args.print_findings:
        print("DEBUG: findings list (id severity):")
        for f in report.findings:
            print(f"  {f.id} {f.severity.value}")

    out_dir = Path(args.out)
    json_path = JSONReporter().write(report, out_dir)
    html_path = HTMLReporter().write(report, out_dir)

    print(f"Health score: {report.health_score}")
    print(f"Findings: {len(report.findings)}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {html_path}")


if __name__ == "__main__":
    main()
