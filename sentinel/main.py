"""Sentinel API.

The /v1/analyze pipeline is built layer-by-layer (see the GitHub issues):
context_gate -> claim_extractor -> fact_verifier -> safety_judge
-> deterministic gate -> signed attestation -> local audit trace.
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sentinel.attest import create_attestation
from sentinel.contracts import AdRequest
from sentinel.integrations.thrad_client import get_ad_request
from sentinel.pipeline import run_pipeline
from sentinel.pipeline.policy import load_policy
from sentinel.tracing import latest_decisions, record_decision


class EscalationDecision(BaseModel):
    trace_id: str
    decision: str
    reviewer: str = "demo"


def cors_origins_from_env() -> list[str]:
    raw = os.environ.get("SENTINEL_CORS_ORIGINS", "*").strip()
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


app = FastAPI(title="Sentinel", version="0.1.0")

# Default wildcard CORS is for local demo/hackathon use. Set
# SENTINEL_CORS_ORIGINS to comma-separated production origins before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_from_env(),
    allow_methods=["*"],
    allow_headers=["*"],
)

if Path("ui").exists():
    app.mount("/demo", StaticFiles(directory="ui", html=True), name="demo")


@app.get("/health")
def health() -> dict:
    return {"success": True, "data": {"status": "ok"}, "error": None}


@app.get("/v1/scenarios")
def scenarios() -> dict:
    items = json.loads(Path("data/scenarios.json").read_text(encoding="utf-8"))
    items.append(
        {
            "id": "grey_zone",
            "conversation": "User: I am comparing budgeting apps.",
            "ad_creative": "BudgetNest is recommended for you based on this conversation.",
            "advertiser": "BudgetNest",
            "expected": "ESCALATE",
        }
    )
    return {"success": True, "data": {"scenarios": items}, "error": None}


@app.get("/v1/policy")
def policy() -> dict:
    return {"success": True, "data": load_policy(), "error": None}


@app.get("/v1/audit/latest")
def audit_latest(limit: int = Query(20, ge=1, le=100)) -> dict:
    return {"success": True, "data": {"records": latest_decisions(limit)}, "error": None}


@app.get("/v1/thrad/mock")
async def thrad_mock(conversation: str = "", scenario_id: str | None = None) -> dict:
    ad = await get_ad_request(conversation, scenario_id)
    return {"success": True, "data": ad.model_dump(mode="json"), "error": None}


@app.post("/v1/escalations")
def escalation(decision: EscalationDecision) -> dict:
    accepted = decision.decision.upper()
    if accepted not in {"APPROVE", "BLOCK"}:
        return {"success": False, "data": None, "error": "decision must be APPROVE or BLOCK"}

    return {
        "success": True,
        "data": {
            "trace_id": decision.trace_id,
            "decision": accepted,
            "reviewer": decision.reviewer,
        },
        "error": None,
    }


@app.post("/v1/analyze")
def analyze(ad: AdRequest) -> dict:
    result = run_pipeline(ad)
    attestation = create_attestation(ad, result)
    trace = record_decision(ad, result, attestation)
    return {
        "success": True,
        "data": {
            "result": result.model_dump(mode="json"),
            "attestation": attestation.model_dump(mode="json"),
            "trace": trace,
        },
        "error": None,
    }
