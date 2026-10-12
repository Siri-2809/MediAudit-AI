
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = BASE_DIR / "reports"


def generate_audit_report(df, flagged_only=True):
    """Prepare and save an auditor-friendly CSV report."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = df.copy()

    if flagged_only and "NEEDS_REVIEW" in report.columns:
        report = report[report["NEEDS_REVIEW"].fillna(False)]

    # Keep the report focused on fields useful to an auditor.
    preferred_columns = [
        "CLM_ID",
        "CLM_PMT_AMT",
        "CLM_FROM_DT",
        "CLM_THRU_DT",
        "CLM_ADMSN_DT",
        "NCH_BENE_DSCHRG_DT",
        "CLM_UTLZTN_DAY_CNT",
        "LENGTH_OF_STAY",
        "ANOMALY_FLAG",
        "ANOMALY_SCORE",
        "RULE_FLAG",
        "RULE_FLAGS",
        "RULE_REASONS",
        "NEEDS_REVIEW",
        "AUDIT_EXPLANATION",
        "RECOMMENDED_CHECK",
    ]

    columns = [col for col in preferred_columns if col in report.columns]
    report = report[columns]

    output_path = REPORTS_DIR / "audit_findings.csv"
    report.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":
    from .data_processing import load_claims, prepare_claims
    from .anomaly_detection import detect_anomalies
    from .audit_rules import apply_audit_rules
    from .explanations import generate_explanations

    claims = prepare_claims(load_claims())
    claims = detect_anomalies(claims)
    claims = apply_audit_rules(claims)
    claims = generate_explanations(claims)

    output_path = generate_audit_report(claims)

    print("Total claims analyzed:", len(claims))
    print("Claims included in report:", int(claims["NEEDS_REVIEW"].sum()))
    print("Report saved to:", output_path)
