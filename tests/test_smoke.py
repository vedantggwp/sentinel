"""Smoke tests — the skeleton runs green from commit one."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from sentinel.attest import create_attestation, verify_attestation, write_private_key
from sentinel.contracts import AdRequest, PipelineResult, Verdict
from sentinel.main import app
from sentinel.mcp_server import verify


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "ok"


def test_contracts_roundtrip():
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    assert ad.ad_id == "x"
    assert Verdict.BLOCK.value == "BLOCK"


def test_analyze_scenarios():
    client = TestClient(app)
    scenarios = json.loads(Path("data/scenarios.json").read_text(encoding="utf-8"))

    for scenario in scenarios:
        response = client.post("/v1/analyze", json=_scenario_payload(scenario))
        body = response.json()

        assert response.status_code == 200
        assert body["success"] is True
        assert body["error"] is None
        assert body["data"]["result"]["verdict"] == scenario["expected"]
        assert body["data"]["result"]["rule_fired"]


def test_attestation_sign_and_verify(tmp_path):
    key_path = tmp_path / "attest_ed25519"
    write_private_key(str(key_path))
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    result = PipelineResult(
        ad_id="x",
        verdict=Verdict.APPROVE,
        scores={"contextual_safety": 5.0},
        rule_fired="approve",
    )

    attestation = create_attestation(ad, result, private_key_path=str(key_path))

    assert verify_attestation(attestation) is True
    tampered = attestation.model_copy(
        update={"result": result.model_copy(update={"rule_fired": "tampered"})}
    )
    assert verify_attestation(tampered) is False


def test_mcp_verify_tool_uses_same_gate():
    attestation = verify(
        ad_id="urgency",
        conversation="User: I'm comparing travel insurance options.",
        ad_creative="LAST CHANCE - only 2 policies left at this price!!!",
        advertiser="TripSure",
    )

    assert attestation.verdict == Verdict.BLOCK
    assert attestation.result.rule_fired == "urgency_manipulation"


def _scenario_payload(scenario: dict) -> dict:
    return {
        "ad_id": scenario["id"],
        "conversation": scenario["conversation"],
        "ad_creative": scenario["ad_creative"],
        "advertiser": scenario.get("advertiser"),
    }
