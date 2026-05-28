#!/usr/bin/env python3
"""Run a minimal Dataset Quality Auditor example from Python.

Usage:
    python quick_audit.py examples/datasets/classification_dirty.csv label
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dataset_quality_auditor.audit.engine import run_audit


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a deterministic audit for a CSV dataset.",
    )
    parser.add_argument("dataset", help="Path to a CSV dataset.")
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional target column name.",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory where audit.json is written.",
    )
    args = parser.parse_args()

    dataset = Path(args.dataset)
    if not dataset.is_file():
        parser.error(f"Dataset not found: {dataset}")

    result = run_audit(
        dataset_path=dataset.as_posix(),
        target_column=args.target,
        output_dir=args.output_dir,
    )
    score = result["score"]
    profile = result["profile"]
    assert isinstance(score, dict)
    assert isinstance(profile, dict)

    print("Dataset Quality Auditor")
    print(f"Dataset: {result['dataset_path']}")
    print(f"Target: {result.get('target_column') or 'not provided'}")
    print(f"Rows: {profile['row_count']}")
    print(f"Columns: {profile['column_count']}")
    print(f"Readiness Score: {score['score']}/{score['max_score']}")
    print(f"Band: {score['score_band']}")
    print(f"Issues: {len(result['issues'])}")
    print(f"Audit JSON written to: {Path(args.output_dir) / 'audit.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
