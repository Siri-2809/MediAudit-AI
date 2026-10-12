from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "claims.csv"

df = pd.read_csv(
    DATA_PATH,
    dtype={"DESYNPUF_ID": str, "CLM_ID": str}
)

print("Dataset shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum().sort_values(ascending=False).head(15))

print("\nPayment statistics:")
print(df["CLM_PMT_AMT"].describe())