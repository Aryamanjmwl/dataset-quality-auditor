from pathlib import Path

from dataset_quality_auditor.contracts.generator import generate_contract, save_contract


def _write_dataset(path: Path) -> None:
    path.write_text(
        "customer_id,age,city,label\n"
        "C001,18,Berlin,0\n"
        "C002,25,Paris,1\n"
        "C003,40,Berlin,0\n"
        "C004,55,Rome,1\n",
        encoding="utf-8",
    )


def test_generate_contract_contains_expected_sections(tmp_path) -> None:
    dataset = tmp_path / "data.csv"
    _write_dataset(dataset)

    contract = generate_contract(dataset, target_column="label")

    assert contract["contract_version"] == "0.1.0"
    assert contract["dataset"]["target_column"] == "label"
    assert contract["dataset"]["row_count_observed"] == 4
    assert "columns" in contract
    assert "age" in contract["columns"]
    assert contract["target"]["name"] == "label"
    assert contract["target"]["classes_observed"] == ["0", "1"]


def test_generate_contract_includes_constraints_and_id_hints(tmp_path) -> None:
    dataset = tmp_path / "data.csv"
    _write_dataset(dataset)

    contract = generate_contract(dataset, target_column="label")
    age = contract["columns"]["age"]
    city = contract["columns"]["city"]
    customer_id = contract["columns"]["customer_id"]

    assert age["logical_type"] == "numeric"
    assert age["constraints"]["min_value"] == 18.0
    assert age["constraints"]["max_value"] == 55.0
    assert city["categorical"]["allowed_values_observed"] == [
        "Berlin",
        "Paris",
        "Rome",
    ]
    assert city["constraints"]["allowed_values"] == ["Berlin", "Paris", "Rome"]
    assert customer_id["uniqueness_hint"] is True
    assert customer_id["requires_human_review"] is True


def test_save_contract_writes_yaml(tmp_path) -> None:
    dataset = tmp_path / "data.csv"
    _write_dataset(dataset)
    contract = generate_contract(dataset, target_column="label")

    output_path = save_contract(contract, tmp_path / "contracts" / "contract.yaml")

    assert output_path.exists()
    assert "contract_version:" in output_path.read_text(encoding="utf-8")
