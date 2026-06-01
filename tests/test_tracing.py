from __future__ import annotations

import json
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient

from sentinel.attest import create_attestation
from sentinel.config import settings
from sentinel.contracts import AdRequest, Attestation, PipelineResult, Verdict
from sentinel.main import app
import sentinel.tracing as tracing


def test_record_decision_persists_local_audit_without_overmind_key(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")
    monkeypatch.setattr(settings, "overmind_api_key", "")

    record = tracing.record_decision(*_decision_fixture())

    assert record["ad_id"] == "trace-test"
    assert record["verdict"] == Verdict.APPROVE.value
    assert tracing.latest_decisions(1)[0]["trace_id"] == record["trace_id"]


def test_overmind_span_emits_when_key_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")
    monkeypatch.setattr(settings, "overmind_api_key", "test-overmind-key")
    monkeypatch.setattr(settings, "overmind_service_name", "sentinel-test")
    monkeypatch.setattr(settings, "overmind_environment", "test")
    calls: dict[str, object] = {}
    span = _FakeSpan()

    def init(api_key: str, service_name: str, environment: str) -> None:
        calls["init"] = {
            "api_key": api_key,
            "service_name": service_name,
            "environment": environment,
        }

    fake_overmind = SimpleNamespace(
        init=init,
        get_tracer=lambda: _FakeTracer(span),
    )
    monkeypatch.setitem(sys.modules, "overmind", fake_overmind)

    record = tracing.record_decision(*_decision_fixture())

    assert calls["init"] == {
        "api_key": "test-overmind-key",
        "service_name": "sentinel-test",
        "environment": "test",
    }
    assert span.name == "sentinel.decision"
    assert span.attributes == {
        "sentinel.ad_id": "trace-test",
        "sentinel.verdict": Verdict.APPROVE.value,
        "sentinel.rule_fired": "passed",
    }
    assert tracing.latest_decisions(1)[0]["trace_id"] == record["trace_id"]


def test_overmind_failure_does_not_block_api_or_local_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(tracing, "AUDIT_PATH", tmp_path / "decisions.jsonl")
    monkeypatch.setattr(settings, "overmind_api_key", "test-overmind-key")

    def init(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("overmind unavailable")

    monkeypatch.setitem(
        sys.modules,
        "overmind",
        SimpleNamespace(init=init, get_tracer=lambda: None),
    )

    response = TestClient(app).post(
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
    assert body["success"] is True
    assert body["data"]["result"]["verdict"] == Verdict.BLOCK.value
    assert body["data"]["result"]["rule_fired"] == "false_claim"
    assert body["data"]["trace"]["trace_id"]

    rows = (tmp_path / "decisions.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    assert json.loads(rows[0])["trace_id"] == body["data"]["trace"]["trace_id"]


def _decision_fixture() -> tuple[AdRequest, PipelineResult, Attestation]:
    ad = AdRequest(
        ad_id="trace-test",
        conversation="User: comparing laptops.",
        ad_creative="Acme Pro 14 starting at $999.",
        advertiser="Acme",
    )
    result = PipelineResult(
        ad_id=ad.ad_id,
        verdict=Verdict.APPROVE,
        scores={"contextual_safety": 5.0},
        rule_fired="passed",
        reason="All deterministic gate checks passed",
    )
    return ad, result, create_attestation(ad, result)


class _FakeSpan:
    def __init__(self) -> None:
        self.name = ""
        self.attributes: dict[str, str] = {}

    def __enter__(self) -> "_FakeSpan":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def set_attribute(self, key: str, value: str) -> None:
        self.attributes[key] = value


class _FakeTracer:
    def __init__(self, span: _FakeSpan) -> None:
        self.span = span

    def start_as_current_span(self, name: str) -> _FakeSpan:
        self.span.name = name
        return self.span
