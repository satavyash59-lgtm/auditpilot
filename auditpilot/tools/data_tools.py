from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "entry_id",
    "date",
    "posted_by",
    "approved_by",
    "account_code",
    "account_name",
    "vendor_id",
    "amount_inr",
    "description",
]


def load_ledger(path: str = "data/ledger.csv") -> dict[str, Any]:
    """
    Load and validate the audit ledger.

    Checks required columns, missing values, duplicate IDs,
    invalid dates, and invalid transaction amounts.
    """

    file_path = Path(path)

    if not file_path.exists():
        return {
            "test": "load_ledger",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": [f"Ledger file not found: {file_path}"],
        }

    try:
        df = pd.read_csv(file_path, dtype={"account_code": str})
    except Exception as exc:
        return {
            "test": "load_ledger",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": [f"Could not read ledger: {exc}"],
        }

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "test": "load_ledger",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {"row_count": len(df)},
            "notes": [f"Missing columns: {missing_columns}"],
        }

    missing_values = int(df[REQUIRED_COLUMNS].isnull().sum().sum())

    duplicate_ids = df.loc[
        df["entry_id"].duplicated(keep=False),
        "entry_id"
    ].astype(str).tolist()

    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = int(parsed_dates.isnull().sum())

    numeric_amounts = pd.to_numeric(
        df["amount_inr"], errors="coerce"
    )
    invalid_amounts = int(numeric_amounts.isnull().sum())

    notes = []

    if missing_values:
        notes.append(f"Missing values found: {missing_values}")

    if duplicate_ids:
        notes.append(f"Duplicate transaction IDs found: {len(duplicate_ids)}")

    if invalid_dates:
        notes.append(f"Invalid dates found: {invalid_dates}")

    if invalid_amounts:
        notes.append(f"Invalid transaction amounts found: {invalid_amounts}")

    status = "PASS" if not notes else "WARNING"

    return {
        "test": "load_ledger",
        "status": status,
        "flagged_ids": sorted(set(duplicate_ids)),
        "stats": {
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_values": missing_values,
            "duplicate_ids": len(set(duplicate_ids)),
            "invalid_dates": invalid_dates,
            "invalid_amounts": invalid_amounts,
            "total_amount_inr": float(numeric_amounts.sum()),
        },
        "notes": notes or ["Ledger loaded and validated successfully."],
    }
def check_trial_balance(
    path: str = "data/trial_balance.csv",
) -> dict[str, Any]:
    """
    Check whether total debits and credits are equal.
    """

    file_path = Path(path)

    if not file_path.exists():
        return {
            "test": "check_trial_balance",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": [f"Trial balance file not found: {file_path}"],
        }

    try:
        df = pd.read_csv(file_path, dtype={"account_code": str})
    except Exception as exc:
        return {
            "test": "check_trial_balance",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": [f"Could not read trial balance: {exc}"],
        }

    required_columns = [
        "account_code",
        "debit_inr",
        "credit_inr",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "test": "check_trial_balance",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": [f"Missing columns: {missing_columns}"],
        }

    debits = pd.to_numeric(df["debit_inr"], errors="coerce")
    credits = pd.to_numeric(df["credit_inr"], errors="coerce")

    if debits.isnull().any() or credits.isnull().any():
        return {
            "test": "check_trial_balance",
            "status": "FAIL",
            "flagged_ids": [],
            "stats": {},
            "notes": ["Invalid or missing debit/credit values found."],
        }

    total_debits = float(debits.sum())
    total_credits = float(credits.sum())
    difference = round(total_debits - total_credits, 2)

    balanced = difference == 0

    return {
        "test": "check_trial_balance",
        "status": "PASS" if balanced else "WARNING",
        "flagged_ids": [],
        "stats": {
            "total_debits_inr": total_debits,
            "total_credits_inr": total_credits,
            "difference_inr": difference,
            "balanced": balanced,
            "account_count": len(df),
        },
        "notes": [
            "Trial balance is balanced."
            if balanced
            else f"Trial balance difference detected: Rs. {difference:,.2f}"
        ],
    }


def benford_test(path="data/ledger.csv"):
    """Analyze first-digit distribution using Benford's Law."""
    import math

    file = Path(path)
    if not file.exists():
        return {"test": "benford_test", "status": "FAIL",
                "flagged_ids": [], "stats": {},
                "notes": ["Ledger file not found."]}

    df = pd.read_csv(file)
    if "amount_inr" not in df.columns:
        return {"test": "benford_test", "status": "FAIL",
                "flagged_ids": [], "stats": {},
                "notes": ["amount_inr column missing."]}

    counts = {str(i): 0 for i in range(1, 10)}
    for value in pd.to_numeric(df["amount_inr"], errors="coerce").dropna():
        digits = str(abs(int(value)))
        first = next((c for c in digits if c in "123456789"), None)
        if first:
            counts[first] += 1

    total = sum(counts.values())
    if total == 0:
        return {"test": "benford_test", "status": "FAIL",
                "flagged_ids": [], "stats": {},
                "notes": ["No valid amounts found."]}

    observed = {d: counts[d] / total for d in counts}
    expected = {str(i): math.log10(1 + 1 / i) for i in range(1, 10)}
    mad = sum(abs(observed[d] - expected[d]) for d in counts) / 9

    return {
        "test": "benford_test", "status": "INFO", "flagged_ids": [],
        "stats": {"valid_transactions": total,
                  "first_digit_counts": counts,
                  "observed_frequencies": observed,
                  "expected_frequencies": expected, "mad": mad},
        "notes": ["Benford analysis is a screening indicator, not proof of fraud."]
    }


def find_duplicates(path="data/ledger.csv"):
    """Find repeated vendor, amount and date combinations."""
    df = pd.read_csv(path)
    required = ["entry_id", "vendor_id", "amount_inr", "date"]
    if not set(required).issubset(df.columns):
        return {"test": "find_duplicates", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Required columns missing."]}

    mask = df.duplicated(["vendor_id", "amount_inr", "date"], keep=False)
    ids = df.loc[mask, "entry_id"].astype(str).tolist()
    return {"test": "find_duplicates", "status": "INFO",
            "flagged_ids": ids, "stats": {"duplicate_rows": len(ids)},
            "notes": ["Repeated vendor/amount/date combinations require review."]}


def find_split_payments(path="data/ledger.csv", threshold=50000):
    """Find groups of small payments to the same vendor on one date."""
    df = pd.read_csv(path)
    required = ["entry_id", "vendor_id", "amount_inr", "date"]
    if not set(required).issubset(df.columns):
        return {"test": "find_split_payments", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Required columns missing."]}

    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    small = df[(df["amount_inr"] > 0) & (df["amount_inr"] < threshold)]
    groups = small.groupby(["vendor_id", "date"]).filter(
        lambda g: len(g) >= 2 and g["amount_inr"].sum() >= threshold
    )
    ids = groups["entry_id"].astype(str).tolist()
    return {"test": "find_split_payments", "status": "INFO",
            "flagged_ids": ids, "stats": {"flagged_rows": len(ids)},
            "notes": ["Potential split-payment groups require review."]}


def find_weekend_round(path="data/ledger.csv"):
    """Find Sunday transactions with round amounts."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    mask = (df["date"].dt.dayofweek == 6) & (df["amount_inr"] % 1000 == 0)
    ids = df.loc[mask, "entry_id"].astype(str).tolist()
    return {"test": "find_weekend_round", "status": "INFO",
            "flagged_ids": ids, "stats": {"flagged_rows": len(ids)},
            "notes": ["Sunday round-amount transactions require review."]}


def check_approval_limits(path="data/ledger.csv", limit=50000):
    """Flag self-approved transactions and transactions above the review limit."""
    df = pd.read_csv(path)
    required = ["entry_id", "posted_by", "approved_by", "amount_inr"]
    if not set(required).issubset(df.columns):
        return {"test": "check_approval_limits", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Required columns missing."]}

    amount = pd.to_numeric(df["amount_inr"], errors="coerce")
    self_approved = df["posted_by"] == df["approved_by"]
    high_value = amount >= limit
    ids = df.loc[self_approved, "entry_id"].astype(str).tolist()
    return {"test": "check_approval_limits", "status": "INFO",
            "flagged_ids": ids,
            "stats": {"self_approved_rows": len(ids),
                      "high_value_rows": int(high_value.sum())},
            "notes": ["Self-approved transactions flagged. High-value transactions are reported separately; threshold alone does not prove a policy violation."]}


def vendor_bank_overlap(vendor_path="data/vendors.csv",
                        employee_path="data/employees.csv"):
    """Find bank accounts shared between vendors and employees."""
    vendors = pd.read_csv(vendor_path, dtype=str)
    employees = pd.read_csv(employee_path, dtype=str)

    if not {"vendor_id", "bank_account"}.issubset(vendors.columns):
        return {"test": "vendor_bank_overlap", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Vendor columns missing."]}

    if "bank_account" not in employees.columns:
        return {"test": "vendor_bank_overlap", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Employee bank column missing."]}

    shared = set(vendors["bank_account"].dropna()) & set(
        employees["bank_account"].dropna()
    )
    ids = vendors.loc[vendors["bank_account"].isin(shared),
                      "vendor_id"].astype(str).tolist()
    return {"test": "vendor_bank_overlap", "status": "INFO",
            "flagged_ids": ids, "stats": {"shared_accounts": len(shared)},
            "notes": ["Shared vendor-employee bank accounts require review."]}


def ratio_table(path="data/financials.csv"):
    """Calculate basic monthly revenue and expense ratios."""
    df = pd.read_csv(path)
    if not {"revenue_inr", "expenses_inr"}.issubset(df.columns):
        return {"test": "ratio_table", "status": "FAIL",
                "flagged_ids": [], "stats": {}, "notes": ["Financial columns missing."]}

    revenue = pd.to_numeric(df["revenue_inr"], errors="coerce").sum()
    expenses = pd.to_numeric(df["expenses_inr"], errors="coerce").sum()
    return {"test": "ratio_table", "status": "INFO", "flagged_ids": [],
            "stats": {"total_revenue_inr": float(revenue),
                      "total_expenses_inr": float(expenses),
                      "expense_to_revenue_ratio": (
                          float(expenses / revenue) if revenue else None
                      )},
            "notes": ["Basic financial ratios calculated."]}
