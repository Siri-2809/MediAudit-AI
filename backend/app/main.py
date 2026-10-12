
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data_processing import load_claims, prepare_claims
from .anomaly_detection import detect_anomalies
from .audit_rules import apply_audit_rules
from .explanations import generate_explanations
from fastapi.responses import FileResponse
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

# Analyze the dataset once when the API starts.
claims = prepare_claims(load_claims())
claims = detect_anomalies(claims)
claims = apply_audit_rules(claims)
claims = generate_explanations(claims)


def to_records(df):
    # Convert missing values and NumPy types to JSON-safe values.
    import json
    return json.loads(df.to_json(orient="records", date_format="iso"))


@app.get("/")
def home():
    return {"message": "MediAudit AI API is running"}


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
    result = claims[claims["CLM_ID"].astype(str) == claim_id]

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
    result = claims[claims["CLM_ID"].astype(str) == claim_id]

    if result.empty:
        raise HTTPException(status_code=404, detail="Claim not found")

    try:
        claim = result.iloc[0].to_dict()
        explanation = explain_claim_with_llm(claim)

        return {
            "claim_id": claim_id,
            "ai_explanation": explanation,
        }

    except Exception as exc:
        # Avoid returning API keys or provider error details to clients.
        print(f"LLM ERROR: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="AI explanation is temporarily unavailable. Check the backend logs.",
        ) from exc

