from pathlib import Path

from dataset_quality_auditor.contracts.generator import generate_contract, save_contract
from dataset_quality_auditor.contracts.validator import validate_dataset


def _write_training_dataset(path: Path) -> None:
    path.write_text(
        "customer_id,age,city,label\n"
        "C001,18,Berlin,0\n"
        "C002,25,Paris,1\n"
        "C003,40,Berlin,0\n"
        "C004,55,Rome,1\n",
        encoding="utf-8",
    )


def _contract_path(tmp_path, dataset: Path) -> Path:
    contract = generate_contract(dataset, target_column="label")
    return save_contract(contract, tmp_path / "contract.yaml")


def test_validate_dataset_passes_for_generation_dataset(tmp_path) -> None:
    dataset = tmp_path / "train.csv"
    _write_training_dataset(dataset)
    contract_path = _contract_path(tmp_path, dataset)

    result = validate_dataset(dataset, contract_path)

    assert result["passed"] is True
    assert result["summary"]["failed_checks"] == 0
    assert result["checks"]


def test_validate_dataset_fails_when_required_column_missing(tmp_path) -> None:
    dataset = tmp_path / "train.csv"
    _write_training_dataset(dataset)
    contract_path = _contract_path(tmp_path, dataset)
    missing = tmp_path / "missing.csv"
    missing.write_text("customer_id,city,label\nC001,Berlin,0\n", encoding="utf-8")

    result = validate_dataset(missing, contract_path)

    assert result["passed"] is False
    assert any(check["rule_id"] == "column_required_age" for check in result["checks"])


def test_validate_dataset_fails_for_unknown_category(tmp_path) -> None:
    dataset = tmp_path / "train.csv"
    _write_training_dataset(dataset)
    contract_path = _contract_path(tmp_path, dataset)
    changed = tmp_path / "changed.csv"
    changed.write_text(
        "customer_id,age,city,label\nC001,20,Madrid,0\n",
        encoding="utf-8",
    )

    result = validate_dataset(changed, contract_path)

    assert result["passed"] is False
    assert any(check["rule_id"] == "allowed_values_city" for check in result["checks"])


def test_validate_dataset_fails_for_numeric_range_violation(tmp_path) -> None:
    dataset = tmp_path / "train.csv"
    _write_training_dataset(dataset)
    contract_path = _contract_path(tmp_path, dataset)
    changed = tmp_path / "changed.csv"
    changed.write_text(
        "customer_id,age,city,label\nC001,99,Berlin,0\n",
        encoding="utf-8",
    )

    result = validate_dataset(changed, contract_path)

    assert result["passed"] is False
    assert any(check["rule_id"] == "max_value_age" for check in result["checks"])
    assert "summary" in result
    assert "checks" in result
