
from io import BytesIO

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .data_processing import load_claims, prepare_claims
from .anomaly_detection import detect_anomalies
from .audit_rules import apply_audit_rules
from .explanations import generate_explanations
from .report_generator import generate_audit_report
from .llm_explainer import explain_claim_with_llm


app = FastAPI(
    title="MediAudit AI API",
    description="Explainable medical claims auditing prototype",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IDENTIFIER_DTYPES = {
    "DESYNPUF_ID": str,
    "CLM_ID": str,
    "PRVDR_NUM": str,
}


def analyze_claims(df):
    """Run the complete audit pipeline on a claims DataFrame."""
    if df.empty:
        raise ValueError("The CSV contains no claim records.")

    if "CLM_ID" not in df.columns:
        raise ValueError("The CSV must contain a CLM_ID column.")

    df = df.copy()
    df["CLM_ID"] = df["CLM_ID"].astype("string").str.strip()

    if df["CLM_ID"].isna().any() or df["CLM_ID"].eq("").any():
        raise ValueError("Every claim must have a non-empty CLM_ID.")


    df = prepare_claims(df)
    df = detect_anomalies(df)
    df = apply_audit_rules(df)
    df = generate_explanations(df)

    return df


# Load and analyze the default dataset at startup.
claims = analyze_claims(prepare_claims(load_claims()))


def to_records(df):
    import json
    return json.loads(
        df.to_json(orient="records", date_format="iso")
    )


@app.get("/")
def home():
    return {"message": "MediAudit AI API is running"}


@app.post("/api/upload")
def upload_claims(file: UploadFile = File(...)):
    global claims

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:
        contents = file.file.read()

        if not contents:
            raise ValueError("The uploaded file is empty.")

        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 50 MB upload limit.",
            )

        uploaded_df = pd.read_csv(
            BytesIO(contents),
            dtype=IDENTIFIER_DTYPES,
        )

        # Process into a temporary DataFrame first.
        # Keep the current dataset if validation or analysis fails.
        analyzed_df = analyze_claims(uploaded_df)

    except HTTPException:
        raise
    except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process the CSV: {exc}",
        ) from exc
    except Exception as exc:
        print(f"UPLOAD ERROR: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=400,
            detail=(
                "The CSV could not be analyzed. Check that it has "
                "the required claim columns and compatible data."
            ),
        ) from exc
    finally:
        file.file.close()

    # Switch datasets only after successful analysis.
    claims = analyzed_df

    return {
        "message": "CSV uploaded and analyzed successfully.",
        "filename": file.filename,
        "total_claims": int(len(claims)),
        "anomaly_flags": int(claims["ANOMALY_FLAG"].sum()),
        "rule_flags": int(claims["RULE_FLAG"].sum()),
        "claims_needing_review": int(claims["NEEDS_REVIEW"].sum()),
        "columns": list(uploaded_df.columns),
    }


@app.get("/api/summary")
def summary():
    return {
        "total_claims": int(len(claims)),
        "anomaly_flags": int(claims["ANOMALY_FLAG"].sum()),
        "rule_flags": int(claims["RULE_FLAG"].sum()),
        "claims_needing_review": int(claims["NEEDS_REVIEW"].sum()),
    }


@app.get("/api/claims")
def get_claims(
    flagged_only: bool = False,
    limit: int = 100,
    offset: int = 0,
):
    if limit < 1 or limit > 1000 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="limit must be 1–1000 and offset must be non-negative",
        )

    result = claims

    if flagged_only:
        result = result[result["NEEDS_REVIEW"]]

    return {
        "total": int(len(result)),
        "items": to_records(result.iloc[offset:offset + limit]),
    }


@app.get("/api/claims/{claim_id}")
def get_claim(claim_id: str):
    claim_ids = claims["CLM_ID"].astype("string").str.strip()
    requested_id = str(claim_id).strip()

    result = claims[claim_ids == requested_id]

    if result.empty:
        raise HTTPException(status_code=404, detail="Claim not found")

    return to_records(result.head(1))[0]


@app.get("/api/report")
def download_report(flagged_only: bool = True):
    output_path = generate_audit_report(
        claims,
        flagged_only=flagged_only,
    )

    return FileResponse(
        path=str(output_path),
        media_type="text/csv",
        filename="audit_findings.csv",
    )


@app.get("/api/claims/{claim_id}/ai-explanation")
def get_ai_explanation(claim_id: str):
    claim_ids = claims["CLM_ID"].astype("string").str.strip()
    requested_id = str(claim_id).strip()

    result = claims[claim_ids == requested_id]

    if result.empty:
        raise HTTPException(status_code=404, detail="Claim not found")

    try:
        explanation = explain_claim_with_llm(
            result.iloc[0].to_dict()
        )
        return {
            "claim_id": claim_id,
            "ai_explanation": explanation,
        }
    except Exception as exc:
        print(f"LLM ERROR: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="AI explanation is temporarily unavailable. Check the backend logs.",
        ) from exc
