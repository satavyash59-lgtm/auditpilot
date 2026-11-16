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
