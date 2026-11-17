from typing import Any

from auditpilot.tools.data_tools import (
    benford_test,
    find_duplicates,
    find_split_payments,
    find_weekend_round,
    check_approval_limits,
    find_ghost_vendors,
    find_prompt_injection,
    vendor_bank_overlap,
    ratio_table,
)


def run_specialist_checks() -> dict[str, Any]:
    """Run all deterministic specialist audit checks locally."""

    return {
        "anomaly_analysis": {
            "benford": benford_test(),
            "duplicates": find_duplicates(),
            "split_payments": find_split_payments(),
            "weekend_round": find_weekend_round(),
            "approval": check_approval_limits(),
            "prompt_injection": find_prompt_injection(),
        },
        "vendor_analysis": {
            "ghost_vendors": find_ghost_vendors(),
            "shared_bank_accounts": vendor_bank_overlap(),
        },
        "financial_ratios": ratio_table(),
    }
