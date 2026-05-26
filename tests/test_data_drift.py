import json
import os
import subprocess
import sys

import pandas as pd

from dqa.checks.data_drift import DataDriftCheck
from dqa.domain import AuditContext


def test_data_drift_summary_when_no_rows(tmp_path):
    ref = tmp_path / "ref.csv"
    cur = tmp_path / "cur.csv"

    # categorical column only, no numeric drift signal
    ref.write_text("a\n.\n")
    cur.write_text("a\n.\n")

    check = DataDriftCheck()
    findings = check.run(
        pd.DataFrame(),
        AuditContext(
            params={
                "reference_path": str(ref),
                "current_path": str(cur),
            }
        ),
    )

    assert len(findings) == 1
    assert findings[0].id in {"DATA_DRIFT_SUMMARY", "DATA_DRIFT_DETECTED"}


def test_cli_debug_passes_ref_cur(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("x\n1\n2\n")

    ref = tmp_path / "ref.csv"
    ref.write_text("x\n1\n1\n")

    cur = tmp_path / "cur.csv"
    cur.write_text("x\n2\n2\n")

    outdir = tmp_path / "out"

    cmd = [
        sys.executable,
        "-m",
        "dqa",
        "audit",
        "--data",
        str(data),
        "--ref",
        str(ref),
        "--cur",
        str(cur),
        "--out",
        str(outdir),
        "--debug",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)

    assert proc.returncode == 0, proc.stderr

    out = proc.stdout
    assert "DEBUG: runner params" in out
    assert "reference_path" in out
    assert "DATA_DRIFT" in out

    report_file = outdir / "report.json"
    assert report_file.exists()

    with report_file.open("r", encoding="utf-8") as f:
        report = json.load(f)

    assert "findings" in report
    assert any(f["id"].startswith("DATA_DRIFT") for f in report["findings"])
