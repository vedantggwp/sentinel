from __future__ import annotations

import asyncio

import httpx
from fastapi.testclient import TestClient

from sentinel.config import settings
from sentinel.integrations import thrad_client
from sentinel.integrations.thrad_client import get_ad_request
from sentinel.main import app


def test_live_thrad_payload_normalizes_to_ad_request(monkeypatch):
    client = _FakeAsyncClient(
        _FakeResponse(
            {
                "seatbid": [
                    {
                        "bid": [
                            {
                                "id": "bid-123",
                                "adm": "SonicMax - #1 rated, 4.9 stars on Amazon!",
                                "adomain": ["SonicMax"],
                                "ext": {"landing_url": "https://example.test/sonic"},
                            }
                        ]
                    }
                ]
            }
        )
    )
    _configure_live_client(monkeypatch, client)

    ad = asyncio.run(get_ad_request("User: recommend headphones.", "false_rating"))

    assert ad.ad_id == "bid-123"
    assert ad.conversation == "User: recommend headphones."
    assert ad.ad_creative == "SonicMax - #1 rated, 4.9 stars on Amazon!"
    assert ad.advertiser == "SonicMax"
    assert ad.landing_url == "https://example.test/sonic"
    assert client.requests == [
        {
            "url": "https://thrad.example/bid",
            "headers": {"Authorization": "Bearer test-thrad-key"},
            "json": {"conversation": "User: recommend headphones."},
        }
    ]


def test_live_thrad_timeout_falls_back_to_fixture(monkeypatch):
    client = _FakeAsyncClient(error=httpx.TimeoutException("timeout"))
    _configure_live_client(monkeypatch, client)

    ad = asyncio.run(get_ad_request("", "false_rating"))

    assert ad.ad_id == "false_rating"
    assert "4.9 stars" in ad.ad_creative


def test_live_thrad_server_error_falls_back_to_fixture(monkeypatch):
    client = _FakeAsyncClient(_FakeResponse({"error": "no bid"}, status_code=500))
    _configure_live_client(monkeypatch, client)

    ad = asyncio.run(get_ad_request("", "false_rating"))

    assert ad.ad_id == "false_rating"
    assert "4.9 stars" in ad.ad_creative


def test_malformed_live_thrad_payload_falls_back_to_fixture(monkeypatch):
    client = _FakeAsyncClient(_FakeResponse({"ad": {"id": "missing-creative"}}))
    _configure_live_client(monkeypatch, client)

    ad = asyncio.run(get_ad_request("", "false_rating"))

    assert ad.ad_id == "false_rating"
    assert "4.9 stars" in ad.ad_creative


def test_thrad_mock_route_survives_malformed_live_payload(monkeypatch):
    client = _FakeAsyncClient(_FakeResponse({"seatbid": [{"bid": [{"id": "bad"}]}]}))
    _configure_live_client(monkeypatch, client)
    api = TestClient(app)

    response = api.get(
        "/v1/thrad/mock",
        params={"conversation": "User: recommend headphones.", "scenario_id": "false_rating"},
    )
    body = response.json()
    analyzed = api.post("/v1/analyze", json=body["data"])

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["ad_id"] == "false_rating"
    assert body["data"]["conversation"] == "User: recommend headphones."
    assert analyzed.status_code == 200
    assert analyzed.json()["data"]["result"]["verdict"] == "BLOCK"


def _configure_live_client(monkeypatch, client: "_FakeAsyncClient") -> None:
    monkeypatch.setattr(settings, "thrad_api_key", "test-thrad-key")
    monkeypatch.setattr(settings, "thrad_api_url", "https://thrad.example/bid")
    monkeypatch.setattr(thrad_client.httpx, "AsyncClient", lambda **_kwargs: client)


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://thrad.example/bid")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("server error", request=request, response=response)


class _FakeAsyncClient:
    def __init__(
        self,
        response: _FakeResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or _FakeResponse({})
        self.error = error
        self.requests: list[dict] = []

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def post(self, url: str, headers: dict, json: dict) -> _FakeResponse:
        self.requests.append({"url": url, "headers": headers, "json": json})
        if self.error:
            raise self.error
        return self.response
