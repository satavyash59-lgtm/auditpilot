import pandas as pd

from auditpilot.tools.data_tools import load_ledger


def test_load_ledger_success():
    result = load_ledger("data/ledger.csv")

    assert result["status"] == "PASS"
    assert result["stats"]["row_count"] == 6000
    assert result["stats"]["missing_values"] == 0
    assert result["stats"]["duplicate_ids"] == 0


def test_load_ledger_missing_file():
    result = load_ledger("data/nonexistent.csv")

    assert result["status"] == "FAIL"
    assert "not found" in result["notes"][0]


def test_load_ledger_missing_columns(tmp_path):
    file_path = tmp_path / "invalid.csv"

    pd.DataFrame({
        "entry_id": ["TXN001"],
        "amount_inr": [5000],
    }).to_csv(file_path, index=False)

    result = load_ledger(str(file_path))

    assert result["status"] == "FAIL"
    assert "Missing columns" in result["notes"][0]
from auditpilot.tools.data_tools import check_trial_balance


def test_trial_balance_detects_gap():
    result = check_trial_balance("data/trial_balance.csv")

    assert result["status"] == "WARNING"
    assert result["stats"]["balanced"] is False
    assert result["stats"]["difference_inr"] == 250000.0


def test_trial_balance_balanced(tmp_path):
    file_path = tmp_path / "balanced.csv"

    pd.DataFrame({
        "account_code": ["1001", "2001"],
        "debit_inr": [50000, 0],
        "credit_inr": [0, 50000],
    }).to_csv(file_path, index=False)

    result = check_trial_balance(str(file_path))

    assert result["status"] == "PASS"
    assert result["stats"]["balanced"] is True


def test_trial_balance_missing_file():
    result = check_trial_balance("data/missing_trial_balance.csv")

    assert result["status"] == "FAIL"
