"""Smoke tests — the skeleton runs green from commit one."""
from fastapi.testclient import TestClient

from sentinel.contracts import AdRequest, Verdict
from sentinel.main import app


def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "ok"


def test_contracts_roundtrip():
    ad = AdRequest(ad_id="x", conversation="hi", ad_creative="buy this")
    assert ad.ad_id == "x"
    assert Verdict.BLOCK.value == "BLOCK"
