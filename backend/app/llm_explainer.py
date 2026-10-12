
import json
import os
from urllib import response

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

MODEL = "gemini-3.8-flash"


def explain_claim_with_llm(claim):
    """
    Generate an auditor-oriented explanation from supplied claim evidence.
    Does not determine whether a claim is fraudulent.
    """
    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the project-root .env file."
        )

    evidence = {
        "claim_id": str(claim.get("CLM_ID", "")),
        "payment": claim.get("CLM_PMT_AMT"),
        "length_of_stay_days": claim.get("LENGTH_OF_STAY"),
        "utilization_days": claim.get("CLM_UTLZTN_DAY_CNT"),
        "anomaly_flag": bool(claim.get("ANOMALY_FLAG", False)),
        "anomaly_score": claim.get("ANOMALY_SCORE"),
        "rule_flags": claim.get("RULE_FLAGS", ""),
        "rule_reasons": claim.get("RULE_REASONS", ""),
    }

    prompt = f"""
You are an assistant supporting human medical-claims auditors.

Analyze ONLY the supplied evidence. This is a synthetic claims dataset.
Do not diagnose patients, invent missing facts, or declare fraud.

Important constraints:
- An anomaly score is not proof of fraud.
- Do not claim a particular feature caused an Isolation Forest flag
  unless that attribution is explicitly supplied.
- Treat configured thresholds as preliminary review criteria,
  not official Medicare billing rules.
- If evidence is insufficient, say so.
- Give practical verification steps for a human auditor.

Claim evidence:
{json.dumps(evidence, default=str)}

Return ONLY valid JSON with these string fields:
{{
  "summary": "A short, claim-specific explanation",
  "evidence": "The supplied values and rules relevant to review",
  "recommended_checks": "Concrete checks for the auditor",
  "limitations": "What cannot be concluded from this evidence"
}}
"""

    response = client.interactions.create(
    model=MODEL,
    input=prompt,
    )

    result = json.loads(response.output_text)

    required_fields = [
        "summary",
        "evidence",
        "recommended_checks",
        "limitations",
    ]

    if not all(
        isinstance(result.get(field), str) for field in required_fields
    ):
        raise ValueError("The LLM response did not match the expected format.")

    return result
