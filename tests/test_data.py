import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load_data():
    ledger = pd.read_csv(DATA / "ledger.csv", dtype={"account_code": str})
    vendors = pd.read_csv(DATA / "vendors.csv")
    employees = pd.read_csv(DATA / "employees.csv")
    ground_truth = pd.read_csv(DATA / "ground_truth.csv")
    trial_balance = pd.read_csv(DATA / "trial_balance.csv")

    return ledger, vendors, employees, ground_truth, trial_balance


def test_ledger_has_6000_rows():
    ledger, *_ = load_data()
    assert len(ledger) == 6000


def test_vendor_count():
    _, vendors, *_ = load_data()
    assert len(vendors) == 120


def test_employee_count():
    _, _, employees, *_ = load_data()
    assert len(employees) == 40


def test_no_duplicate_entry_ids():
    ledger, *_ = load_data()
    assert ledger["entry_id"].is_unique


def test_account_mapping():
    ledger, *_ = load_data()

    mapping = {
        "5001": "Office Expenses",
        "5002": "Travel Expenses",
        "5003": "IT Expenses",
        "5004": "Professional Fees",
        "4001": "Sales Revenue",
        "4002": "Service Revenue"
    }

    expected = ledger["account_code"].map(mapping)
    assert expected.notna().all()
    assert (expected == ledger["account_name"]).all()


def test_duplicate_payments():
    ledger, _, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "duplicate_payment"
    ]

    assert len(flagged) == 20

    records = ledger[
        ledger["entry_id"].isin(flagged["entry_id"])
    ]

    assert records.duplicated(
        subset=[
            "date", "posted_by", "approved_by",
            "account_code", "vendor_id", "amount_inr",
            "description"
        ],
        keep=False
    ).all()


def test_split_payments():
    ledger, _, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "split_payment"
    ]

    assert len(flagged) == 18

    records = ledger[ledger["entry_id"].isin(flagged["entry_id"])]

    assert (records["amount_inr"] == 49000).all()
    assert records.groupby("description").size().eq(3).all()


def test_ghost_vendors():
    ledger, vendors, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "ghost_vendor"
    ]

    vendor_ids = set(vendors["vendor_id"])
    records = ledger[ledger["entry_id"].isin(flagged["entry_id"])]

    assert len(flagged) == 5
    assert set(records["vendor_id"]).isdisjoint(vendor_ids)


def test_shared_bank_accounts():
    _, vendors, employees, _, _ = load_data()

    shared = set(vendors["bank_account"]) & set(employees["bank_account"])

    assert len(shared) == 3


def test_self_approved():
    ledger, _, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "self_approved"
    ]

    records = ledger[ledger["entry_id"].isin(flagged["entry_id"])]

    assert len(flagged) == 8
    assert (records["posted_by"] == records["approved_by"]).all()


def test_sunday_round_payments():
    ledger, _, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "sunday_round_payment"
    ]

    records = ledger[ledger["entry_id"].isin(flagged["entry_id"])]

    dates = pd.to_datetime(records["date"])

    assert len(flagged) == 12
    assert (dates.dt.day_of_week == 6).all()
    assert (records["amount_inr"] == 50000).all()


def test_prompt_injection():
    ledger, _, _, ground_truth, _ = load_data()

    flagged = ground_truth[
        ground_truth["anomaly_type"] == "prompt_injection"
    ]

    records = ledger[ledger["entry_id"].isin(flagged["entry_id"])]

    assert len(flagged) == 4
    assert records["description"].str.contains(
        "ignore|override|reveal", case=False, regex=True
    ).all()


def test_trial_balance_gap():
    _, _, _, _, trial_balance = load_data()

    debit = trial_balance["debit_inr"].sum()
    credit = trial_balance["credit_inr"].sum()

    assert debit != credit


def test_ground_truth_has_70_records():
    *_, ground_truth, _ = load_data()
    assert len(ground_truth) == 70
