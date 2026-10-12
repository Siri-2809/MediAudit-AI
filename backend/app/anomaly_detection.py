import pandas as pd
from sklearn.ensemble import IsolationForest

from .data_processing import load_claims, prepare_claims

FEATURES = [
    "CLM_PMT_AMT",
    "NCH_PRMRY_PYR_CLM_PD_AMT",
    "CLM_PASS_THRU_PER_DIEM_AMT",
    "CLM_UTLZTN_DAY_CNT",
    "LENGTH_OF_STAY",
]


def detect_anomalies(df):
    df = df.copy()

    # Keep only features available in this dataset.
    features = [col for col in FEATURES if col in df.columns]

    # Convert invalid values to missing and handle them for modeling.
    X = df[features].apply(pd.to_numeric, errors="coerce")
    X = X.replace([float("inf"), float("-inf")], float("nan"))

    # Median imputation for missing numeric values.
    X = X.fillna(X.median()).fillna(0)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )

    predictions = model.fit_predict(X)

    df["ANOMALY_FLAG"] = predictions == -1
    df["ANOMALY_SCORE"] = -model.decision_function(X)

    return df


if __name__ == "__main__":
    claims = load_claims()
    claims = prepare_claims(claims)

    results = detect_anomalies(claims)

    print("Total claims:", len(results))
    print("Flagged claims:", results["ANOMALY_FLAG"].sum())

    print("\nTop 10 unusual claims:")
    print(
        results.loc[
            results["ANOMALY_FLAG"],
            ["CLM_ID", "CLM_PMT_AMT", "LENGTH_OF_STAY", "ANOMALY_SCORE"],
        ]
        .sort_values("ANOMALY_SCORE", ascending=False)
        .head(10)
        .to_string(index=False)
    )

    results.to_csv("reports/anomaly_results.csv", index=False)
    print("\nSaved results to reports/anomaly_results.csv")