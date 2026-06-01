import hashlib

from sentinel.config import settings
from sentinel.contracts import AdRequest, Verdict
from sentinel.pipeline import claims as claims_module
from sentinel.pipeline.claims import extract_claims, verify_claims
from sentinel.pipeline.core import run_pipeline


class FakeTavilyClient:
    calls: list[dict] = []
    response: dict = {}
    error: Exception | None = None

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, query: str, **kwargs) -> dict:
        self.__class__.calls.append(
            {"api_key": self.api_key, "query": query, "kwargs": kwargs}
        )
        if self.__class__.error:
            raise self.__class__.error
        return self.__class__.response

    async def close(self) -> None:
        return None


def test_tavily_rating_mismatch_marks_claim_false(monkeypatch):
    _mock_tavily(
        monkeypatch,
        {
            "results": [
                {
                    "url": "https://reviews.example/sonicmax",
                    "title": "SonicMax reviews",
                    "content": (
                        "The ad says 4.9 stars, "
                        "but reviews average 3.2 stars."
                    ),
                }
            ]
        },
    )
    ad = _rating_ad()

    verified = verify_claims(ad, extract_claims(ad.ad_creative))
    rating = _rating_claim(verified)

    assert FakeTavilyClient.calls == [
        {
            "api_key": "test-tavily-key",
            "query": "SonicMax 4.9 stars actual customer rating review",
            "kwargs": {
                "search_depth": "advanced",
                "include_answer": "advanced",
                "max_results": 5,
                "timeout": 10,
            },
        }
    ]
    assert rating.verified is False
    assert rating.actual_value == "3.2 stars"
    assert rating.source_url == "https://reviews.example/sonicmax"
    assert rating.source_hash == hashlib.sha256(
        b"https://reviews.example/sonicmax"
    ).hexdigest()


def test_tavily_matching_rating_marks_claim_true(monkeypatch):
    _mock_tavily(
        monkeypatch,
        {
            "results": [
                {
                    "url": "https://reviews.example/sonicmax",
                    "content": "Verified storefront rating: 4.8 stars.",
                }
            ]
        },
    )

    rating = _rating_claim(
        verify_claims(_rating_ad(), extract_claims("4.9 stars"))
    )

    assert rating.verified is True
    assert rating.actual_value == "4.8 stars"
    assert rating.source_url == "https://reviews.example/sonicmax"


def test_tavily_failure_falls_back_to_offline_fixture(monkeypatch):
    _mock_tavily(monkeypatch, {}, error=TimeoutError("tavily timeout"))

    rating = _rating_claim(
        verify_claims(_rating_ad(), extract_claims("4.9 stars"))
    )

    assert rating.verified is False
    assert rating.actual_value == "3.2 stars"
    assert rating.source_url == "offline://claim/rating-overstated"
    assert rating.source_hash == hashlib.sha256(
        b"offline://claim/rating-overstated"
    ).hexdigest()


def test_no_tavily_key_uses_offline_fixture(monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "")
    monkeypatch.setattr(
        claims_module,
        "AsyncTavilyClient",
        lambda api_key: (_ for _ in ()).throw(AssertionError("network attempted")),
    )

    rating = _rating_claim(
        verify_claims(_rating_ad(), extract_claims("4.9 stars"))
    )

    assert rating.verified is False
    assert rating.source_url == "offline://claim/rating-overstated"


def test_tavily_false_rating_still_blocks_through_deterministic_gate(monkeypatch):
    _mock_tavily(
        monkeypatch,
        {
            "results": [
                {
                    "url": "https://reviews.example/sonicmax",
                    "content": "Independent review average: 3.2 stars.",
                }
            ]
        },
    )

    result = run_pipeline(_rating_ad())

    assert result.verdict is Verdict.BLOCK
    assert result.rule_fired == "false_claim"
    assert result.claims[0].verified is False


def _mock_tavily(monkeypatch, response: dict, error: Exception | None = None) -> None:
    FakeTavilyClient.calls = []
    FakeTavilyClient.response = response
    FakeTavilyClient.error = error
    monkeypatch.setattr(settings, "tavily_api_key", "test-tavily-key")
    monkeypatch.setattr(claims_module, "AsyncTavilyClient", FakeTavilyClient)


def _rating_ad() -> AdRequest:
    return AdRequest(
        ad_id="false-rating",
        conversation="User: recommend good noise-cancelling headphones.",
        ad_creative="SonicMax - 4.9 stars on Amazon!",
        advertiser="SonicMax",
    )


def _rating_claim(claims):
    return next(claim for claim in claims if claim.type == "rating")
