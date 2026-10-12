
import pandas as pd


def generate_explanations(df):
    df = df.copy()

    explanations = []
    recommended_checks = []

    for _, row in df.iterrows():
        reasons = []
        checks = []

        payment = pd.to_numeric(
            pd.Series([row.get("CLM_PMT_AMT")]), errors="coerce"
        ).iloc[0]

        stay = pd.to_numeric(
            pd.Series([row.get("LENGTH_OF_STAY")]), errors="coerce"
        ).iloc[0]

        # Explain the ML flag without claiming to know which feature
        # caused Isolation Forest to flag the claim.
        if bool(row.get("ANOMALY_FLAG", False)):
            reasons.append(
                "Isolation Forest identified this claim as unusual "
                "relative to the claims analyzed."
            )

            checks.append(
                "Compare the claim's payment, length of stay, and other "
                "available fields with similar claims and supporting records."
            )

            # Contextual clues for the auditor, not proven model causes.
            if pd.notna(payment) and payment == 0:
                reasons.append(
                    "The recorded payment is 0; this may warrant "
                    "verification of the claim's payment status."
                )
                checks.append(
                    "Verify whether zero payment is expected, including "
                    "whether the claim was denied, adjusted, or otherwise "
                    "validly recorded."
                )

            elif pd.notna(payment) and payment < 0:
                reasons.append(
                    "The recorded payment is negative and requires context."
                )
                checks.append(
                    "Check whether the amount represents a valid "
                    "adjustment, reversal, or other transaction."
                )

            if pd.notna(stay) and stay > 30:
                reasons.append(
                    f"The recorded length of stay is {int(stay)} days, "
                    "which exceeds the preliminary 30-day review threshold."
                )
                checks.append(
                    "Verify admission and discharge dates and review "
                    "supporting hospital records."
                )

            if pd.notna(payment) and payment > 30000:
                reasons.append(
                    f"The recorded payment is {payment:,.2f}, above the "
                    "preliminary review threshold of 30,000."
                )
                checks.append(
                    "Compare the reimbursement amount with claim "
                    "documentation and applicable payment details."
                )

        # Include the transparent rule findings.
        rule_flags = row.get("RULE_FLAGS", "")
        rule_reasons = row.get("RULE_REASONS", "")

        rule_flags = (
            str(rule_flags).strip()
            if pd.notna(rule_flags)
            else ""
        )
        rule_reasons = (
            str(rule_reasons).strip()
            if pd.notna(rule_reasons)
            else ""
        )

        if rule_flags:
            reasons.extend(
                part.strip()
                for part in rule_reasons.split(";")
                if part.strip()
            )

            if "HIGH_PAYMENT" in rule_flags:
                checks.append(
                    "Verify the reimbursement amount against the claim "
                    "documentation and applicable payment details."
                )

            if "NEGATIVE_PAYMENT" in rule_flags:
                checks.append(
                    "Check whether the negative payment represents a "
                    "valid adjustment or reversal."
                )

            if "LONG_STAY" in rule_flags:
                checks.append(
                    "Verify admission and discharge dates and supporting "
                    "hospital records."
                )

            if "ZERO_PAYMENT" in rule_flags:
                checks.append(
                    "Verify whether zero payment is expected, including whether "
                    "the claim was denied, adjusted, or otherwise validly recorded."
                )

            if "STAY_DAYS_MISMATCH" in rule_flags:
                checks.append(
                    "Compare the date-derived length of stay with the recorded "
                    "utilization day count and verify the dataset's field definitions."
                )

        # Remove duplicate messages while preserving order.
        reasons = list(dict.fromkeys(reasons))
        checks = list(dict.fromkeys(checks))

        explanations.append(
            " ".join(reasons)
            if reasons
            else "No anomaly or configured audit rule was triggered."
        )

        recommended_checks.append(
            " ".join(checks)
            if checks
            else "No specific check was triggered by the current rules."
        )

    df["AUDIT_EXPLANATION"] = explanations
    df["RECOMMENDED_CHECK"] = recommended_checks

    df["NEEDS_REVIEW"] = (
        df["ANOMALY_FLAG"].fillna(False).astype(bool)
        | df["RULE_FLAG"].fillna(False).astype(bool)
    )

    return df


if __name__ == "__main__":
    from .data_processing import load_claims, prepare_claims
    from .anomaly_detection import detect_anomalies
    from .audit_rules import apply_audit_rules

    claims = prepare_claims(load_claims(nrows=10000))
    claims = detect_anomalies(claims)
    claims = apply_audit_rules(claims)
    results = generate_explanations(claims)

    print("Total claims:", len(results))
    print("Claims needing review:", int(results["NEEDS_REVIEW"].sum()))

    columns = [
        "CLM_ID",
        "CLM_PMT_AMT",
        "LENGTH_OF_STAY",
        "ANOMALY_FLAG",
        "RULE_FLAGS",
        "AUDIT_EXPLANATION",
        "RECOMMENDED_CHECK",
    ]

    print(
        results.loc[results["NEEDS_REVIEW"], columns]
        .head(5)
        .to_string(index=False)
    )

    from .report_generator import generate_audit_report

    path = generate_audit_report(results)
    print("\nSaved report to:", path)
