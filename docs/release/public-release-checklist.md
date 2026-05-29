# Public Release Checklist

Use this checklist before opening the repository publicly or creating a release
tag.

## Validation

- [ ] Run `python -m pip install -e ".[dev]"`.
- [ ] Run `ruff check .`.
- [ ] Run `pytest`.
- [ ] Run `pytest --cov=dataset_quality_auditor --cov-report=term-missing`.
- [ ] Run `python -m build`.
- [ ] Run `python -m twine check dist/*`.
- [ ] Run `python -m pip_audit` or review the dependency audit workflow result.
- [ ] Run `git diff --check`.
- [ ] Confirm GitHub Actions passes on Python 3.10, 3.11, and 3.12.
  Dependency audit is initially informational and may be non-blocking.
- [ ] Confirm generated artifacts such as `dist/`, `build/`, `*.egg-info/`,
      `reports/`, and test caches are not staged.

## Documentation

- [ ] README install and quickstart commands are copy-pasteable.
- [ ] README examples use committed files under `examples/`.
- [ ] README clearly states current input support is local CSV files.
- [ ] Docs do not claim PyPI publishing, production readiness, or coverage
      numbers unless those are true.

## Examples

- [ ] `quick_audit.py` runs against a committed example dataset.
- [ ] Curated example reports, contracts, and validation results avoid local
      machine paths.
- [ ] Generated runtime folders such as `reports/` and `contracts/` are not
      committed.

## Community Files

- [ ] `SECURITY.md` describes how to report vulnerabilities.
- [ ] Bug report and feature request templates are present.
- [ ] Pull request template is present.
- [ ] License file is present.

## Release Notes

- [ ] Changelog entry is updated.
- [ ] Release notes are prepared.
- [ ] The release tag matches the package version.
