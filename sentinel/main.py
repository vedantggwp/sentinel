"""Sentinel API.

The /v1/analyze pipeline is built layer-by-layer (see the GitHub issues):
context_gate -> claim_extractor -> fact_verifier -> safety_judge
-> deterministic gate -> signed attestation -> Overmind trace.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sentinel.attest import create_attestation
from sentinel.contracts import AdRequest
from sentinel.pipeline import run_pipeline

app = FastAPI(title="Sentinel", version="0.1.0")

# Hackathon demo only — tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"success": True, "data": {"status": "ok"}, "error": None}


@app.post("/v1/analyze")
def analyze(ad: AdRequest) -> dict:
    result = run_pipeline(ad)
    attestation = create_attestation(ad, result)
    return {
        "success": True,
        "data": {
            "result": result.model_dump(mode="json"),
            "attestation": attestation.model_dump(mode="json"),
        },
        "error": None,
    }
