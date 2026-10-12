
import pandas as pd


def apply_audit_rules(df):
    df = df.copy()

    df["RULE_FLAGS"] = ""
    df["RULE_REASONS"] = ""

    def add_flag(mask, flag, reason):
        mask = mask.fillna(False)
        df.loc[mask, "RULE_FLAGS"] = df.loc[mask, "RULE_FLAGS"].apply(
            lambda value: f"{value}; {flag}" if value else flag
        )
        df.loc[mask, "RULE_REASONS"] = df.loc[mask, "RULE_REASONS"].apply(
            lambda value: f"{value} {reason}" if value else reason
        )

    if "CLM_PMT_AMT" in df.columns:
        payment = pd.to_numeric(df["CLM_PMT_AMT"], errors="coerce")

        add_flag(
            payment > 30000,
            "HIGH_PAYMENT",
            "Payment exceeds the preliminary review threshold of 30,000; "
            "verify reimbursement details.",
        )

        add_flag(
            payment < 0,
            "NEGATIVE_PAYMENT",
            "Negative payment requires checking for a valid adjustment or reversal.",
        )

        add_flag(
            payment == 0,
            "ZERO_PAYMENT",
            "Zero payment requires checking the claim's payment status and documentation.",
        )

    if "LENGTH_OF_STAY" in df.columns:
        stay = pd.to_numeric(df["LENGTH_OF_STAY"], errors="coerce")

        add_flag(
            stay > 30,
            "LONG_STAY",
            "Hospital stay exceeds the preliminary 30-day review threshold; "
            "verify dates and supporting records.",
        )

        # Compare utilization days with the date-derived length of stay.
        if "CLM_UTLZTN_DAY_CNT" in df.columns:
            utilization_days = pd.to_numeric(
                df["CLM_UTLZTN_DAY_CNT"], errors="coerce"
            )

            valid = stay.notna() & utilization_days.notna()

            add_flag(
                valid & (stay != utilization_days),
                "STAY_DAYS_MISMATCH",
                "Date-derived length of stay differs from the recorded "
                "utilization day count; verify field definitions and records.",
            )

    df["RULE_FLAG"] = df["RULE_FLAGS"].ne("")

    return df


if __name__ == "__main__":
    from .data_processing import load_claims, prepare_claims
    from .anomaly_detection import detect_anomalies
    from .explanations import generate_explanations
    from .report_generator import generate_audit_report

    claims = prepare_claims(load_claims(nrows=10000))
    claims = detect_anomalies(claims)
    claims = apply_audit_rules(claims)
    claims = generate_explanations(claims)

    print("Total claims:", len(claims))
    print("\nRule counts:")

    for rule in [
        "HIGH_PAYMENT",
        "LONG_STAY",
        "NEGATIVE_PAYMENT",
        "ZERO_PAYMENT",
        "STAY_DAYS_MISMATCH",
    ]:
        count = claims["RULE_FLAGS"].apply(
            lambda flags: rule in flags.split("; ")
        ).sum()
        print(f"{rule}: {count}")

    print("\nClaims needing review:", int(claims["NEEDS_REVIEW"].sum()))

    path = generate_audit_report(claims)
    print("Saved report:", path)
