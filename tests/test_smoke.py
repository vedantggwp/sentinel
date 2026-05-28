"""Smoke tests — the skeleton runs green from commit one."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

import sentinel.attest as attest
from sentinel.attest import create_attestation, verify_attestation, write_private_key
from sentinel.contracts import AdRequest, PipelineResult, Verdict
from sentinel.main import app
from sentinel.mcp_server import mcp, verify
import sentinel.tracing as tracing


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "ok"


def test_contracts_roundtrip():
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    assert ad.ad_id == "x"
    assert Verdict.BLOCK.value == "BLOCK"


def test_analyze_scenarios(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")
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
        assert body["data"]["trace"]["trace_id"]


def test_demo_routes_and_escalation(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")
    client = TestClient(app)

    demo = client.get("/demo/")
    scenarios = client.get("/v1/scenarios").json()["data"]["scenarios"]
    grey_zone = next(item for item in scenarios if item["id"] == "grey_zone")
    analyzed = client.post("/v1/analyze", json=_scenario_payload(grey_zone)).json()
    reviewed = client.post(
        "/v1/escalations",
        json={
            "trace_id": analyzed["data"]["trace"]["trace_id"],
            "decision": "BLOCK",
            "reviewer": "test",
        },
    ).json()
    audit = client.get("/v1/audit/latest").json()

    assert demo.status_code == 200
    assert analyzed["data"]["result"]["verdict"] == "ESCALATE"
    assert reviewed["data"]["decision"] == "BLOCK"
    assert audit["data"]["records"][0]["rule_fired"] == "grey_zone"


def test_thrad_mock_returns_ad_request():
    client = TestClient(app)
    body = client.get("/v1/thrad/mock", params={"scenario_id": "false_rating"}).json()

    assert body["success"] is True
    assert body["data"]["ad_id"] == "false_rating"
    assert "4.9 stars" in body["data"]["ad_creative"]


def test_attestation_sign_and_verify(tmp_path):
    key_path = tmp_path / "attest_ed25519"
    write_private_key(str(key_path))
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    result = PipelineResult(
        ad_id="x",
        verdict=Verdict.APPROVE,
        scores={
            "contextual_safety": 5.0,
            "context_classifier_available": 1.0,
            "context_classifier_confidence": 0.8,
            "context_classifier_label_index": 7.0,
        },
        rule_fired="approve",
    )

    attestation = create_attestation(ad, result, private_key_path=str(key_path))

    assert verify_attestation(attestation) is True
    assert "context_classifier" in attestation.models_used
    assert attestation.models_used["context_classifier_prediction"] == (
        "H:purchasable_products@0.8000"
    )
    tampered = attestation.model_copy(
        update={"result": result.model_copy(update={"rule_fired": "tampered"})}
    )
    assert verify_attestation(tampered) is False


def test_attestation_accepts_escaped_pem_env(tmp_path, monkeypatch):
    key_path = tmp_path / "attest_ed25519"
    write_private_key(str(key_path))
    monkeypatch.setattr(
        attest.settings,
        "attestation_private_key_pem",
        key_path.read_text(encoding="utf-8").replace("\n", "\\n"),
    )
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    result = PipelineResult(
        ad_id="x",
        verdict=Verdict.APPROVE,
        scores={"contextual_safety": 5.0},
        rule_fired="approve",
    )

    attestation = create_attestation(
        ad, result, private_key_path=str(tmp_path / "missing")
    )

    assert verify_attestation(attestation) is True


def test_mcp_verify_tool_uses_same_gate():
    attestation = verify(
        ad_id="urgency",
        conversation="User: I'm comparing travel insurance options.",
        ad_creative="LAST CHANCE - only 2 policies left at this price!!!",
        advertiser="TripSure",
    )

    assert attestation.verdict == Verdict.BLOCK
    assert attestation.result.rule_fired == "urgency_manipulation"


def test_mcp_server_settings_are_deploy_safe():
    assert mcp.settings.host == "0.0.0.0"
    assert mcp.settings.port == 8000
    assert mcp.settings.stateless_http is True
    assert mcp.settings.json_response is True


def _scenario_payload(scenario: dict) -> dict:
    return {
        "ad_id": scenario["id"],
        "conversation": scenario["conversation"],
        "ad_creative": scenario["ad_creative"],
        "advertiser": scenario.get("advertiser"),
    }
