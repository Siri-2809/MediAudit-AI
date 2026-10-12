from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "claims.csv"


def load_claims(nrows=None):
    """Load inpatient claims while preserving claim identifiers."""
    df = pd.read_csv(
        DATA_PATH,
        nrows=nrows,
        dtype={
            "DESYNPUF_ID": str,
            "CLM_ID": str,
            "PRVDR_NUM": str,
        },
    )
    return df


def prepare_claims(df):
    """Prepare basic numerical features for anomaly detection."""
    df = df.copy()

    numeric_columns = [
        "CLM_PMT_AMT",
        "NCH_PRMRY_PYR_CLM_PD_AMT",
        "CLM_PASS_THRU_PER_DIEM_AMT",
        "NCH_BENE_IP_DDCTBL_AMT",
        "NCH_BENE_PTA_COINSRNC_LBLTY_AM",
        "NCH_BENE_BLOOD_DDCTBL_LBLTY_AM",
        "CLM_UTLZTN_DAY_CNT",
    ]

    available_columns = [
        col for col in numeric_columns if col in df.columns
    ]

    for col in available_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derive length of stay where dates are available.
    if {"CLM_ADMSN_DT", "NCH_BENE_DSCHRG_DT"}.issubset(df.columns):
        admission = pd.to_datetime(
            df["CLM_ADMSN_DT"].astype("Int64").astype(str),
            format="%Y%m%d",
            errors="coerce",
        )
        discharge = pd.to_datetime(
            df["NCH_BENE_DSCHRG_DT"].astype("Int64").astype(str),
            format="%Y%m%d",
            errors="coerce",
        )

        df["LENGTH_OF_STAY"] = (discharge - admission).dt.days

    return df


if __name__ == "__main__":
    claims = load_claims(nrows=10000)
    prepared = prepare_claims(claims)

    print("Loaded shape:", claims.shape)
    print("Prepared shape:", prepared.shape)
    print("\nAvailable audit features:")

    candidates = [
        "CLM_PMT_AMT",
        "NCH_PRMRY_PYR_CLM_PD_AMT",
        "CLM_PASS_THRU_PER_DIEM_AMT",
        "CLM_UTLZTN_DAY_CNT",
        "LENGTH_OF_STAY",
    ]

    for col in candidates:
        if col in prepared.columns:
            print(f"\n{col}")
            print(prepared[col].describe())