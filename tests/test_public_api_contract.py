from __future__ import annotations

from fastapi.testclient import TestClient

from sentinel.attest import verify_attestation, write_private_key
from sentinel.config import settings
from sentinel.contracts import Attestation, Verdict
from sentinel.main import app
from sentinel.mcp_server import verify as mcp_verify
import sentinel.tracing as tracing


client = TestClient(app)


def test_public_read_routes_keep_success_envelope(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")

    for path in ["/health", "/v1/policy", "/v1/scenarios", "/v1/audit/latest"]:
        response = client.get(path)
        body = response.json()

        assert response.status_code == 200
        assert set(body) == {"success", "data", "error"}
        assert body["success"] is True
        assert body["data"] is not None
        assert body["error"] is None


def test_policy_route_exposes_gate_contract():
    body = client.get("/v1/policy").json()["data"]

    assert "mental_health" in body["ineligible_contexts"]
    assert "claim_truthfulness" in body["dimensions"]
    assert body["block_if_overall_below"] == 3.0
    assert body["escalate_band"] == [2.5, 3.5]


def test_scenarios_route_includes_demo_and_review_cases():
    scenarios = client.get("/v1/scenarios").json()["data"]["scenarios"]
    by_id = {scenario["id"]: scenario for scenario in scenarios}

    assert by_id["false_rating"]["expected"] == Verdict.BLOCK.value
    assert by_id["grey_zone"]["expected"] == Verdict.ESCALATE.value


def test_analyze_contract_persists_audit_record_and_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")

    response = client.post(
        "/v1/analyze",
        json={
            "ad_id": "false_rating",
            "conversation": "User: recommend good noise-cancelling headphones.",
            "ad_creative": "SonicMax - #1 rated, 4.9 stars on Amazon!",
            "advertiser": "SonicMax",
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert set(body) == {"success", "data", "error"}
    assert body["success"] is True
    assert body["data"]["result"]["verdict"] == Verdict.BLOCK.value
    assert body["data"]["result"]["rule_fired"] == "false_claim"
    false_claim = next(
        claim
        for claim in body["data"]["result"]["claims"]
        if claim["verified"] is False
    )
    assert false_claim["source_url"]
    assert false_claim["source_hash"]
    assert body["data"]["attestation"]["ad_id"] == "false_rating"
    assert body["data"]["trace"]["ad_id"] == "false_rating"
    assert body["data"]["trace"]["rule_fired"] == "false_claim"
    trace_claim = next(
        claim
        for claim in body["data"]["trace"]["claims"]
        if claim["verified"] is False
    )
    assert trace_claim["source_hash"] == false_claim["source_hash"]

    audit = client.get("/v1/audit/latest", params={"limit": 1}).json()["data"]
    assert len(audit["records"]) == 1
    assert audit["records"][0]["trace_id"] == body["data"]["trace"]["trace_id"]


def test_audit_latest_rejects_out_of_range_limits():
    assert client.get("/v1/audit/latest", params={"limit": 0}).status_code == 422
    assert client.get("/v1/audit/latest", params={"limit": 101}).status_code == 422


def test_escalation_contract_accepts_only_final_verdicts():
    accepted = client.post(
        "/v1/escalations",
        json={"trace_id": "trace-1", "decision": "approve", "reviewer": "reviewer"},
    ).json()
    rejected = client.post(
        "/v1/escalations",
        json={"trace_id": "trace-1", "decision": "ESCALATE", "reviewer": "reviewer"},
    ).json()

    assert accepted == {
        "success": True,
        "data": {
            "trace_id": "trace-1",
            "decision": Verdict.APPROVE.value,
            "reviewer": "reviewer",
        },
        "error": None,
    }
    assert rejected == {
        "success": False,
        "data": None,
        "error": "decision must be APPROVE or BLOCK",
    }


def test_mcp_verify_contract_and_signature(tmp_path, monkeypatch):
    key_path = tmp_path / "attest_ed25519"
    write_private_key(str(key_path))
    monkeypatch.setattr(
        settings,
        "attestation_private_key_path",
        str(key_path),
    )
    monkeypatch.setattr(
        settings,
        "attestation_private_key_pem",
        "",
    )

    attestation = mcp_verify(
        ad_id="false_rating",
        conversation="User: recommend good noise-cancelling headphones.",
        ad_creative="SonicMax - #1 rated, 4.9 stars on Amazon!",
        advertiser="SonicMax",
    )

    assert attestation.verdict == Verdict.BLOCK
    assert attestation.result.rule_fired == "false_claim"
    assert attestation.signature
    assert verify_attestation(attestation) is True

    tampered = attestation.model_copy(
        update={
            "result": attestation.result.model_copy(update={"rule_fired": "tampered"})
        }
    )
    assert verify_attestation(Attestation.model_validate(tampered)) is False
