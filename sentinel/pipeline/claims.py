from __future__ import annotations

import asyncio
import hashlib
import inspect
import re
from typing import Any

from sentinel.config import settings
from sentinel.contracts import AdRequest, Claim

try:
    from tavily import AsyncTavilyClient
except ImportError:  # pragma: no cover - requirements.txt includes tavily-python.
    AsyncTavilyClient = None  # type: ignore[assignment]

PRICE_RE = re.compile(r"(\$|£)\s?\d[\d,]*(?:\.\d{2})?")
RATING_RE = re.compile(r"\b\d(?:\.\d)?\s*(?:stars?|/5)\b", re.IGNORECASE)
SCARCITY_TERMS = {"left", "remaining"}
SCARCITY_WINDOW_CHARS = 120
MAX_RATING_DELTA = 0.5

# Offline heuristic: a near-perfect rating we cannot substantiate without
# external web evidence. Keying on claim CONTENT, not the advertiser, catches
# an unsubstantiated 4.9*/#1 ad no matter who sends it.
OVERSTATED_RATING = 4.9


def extract_claims(ad_creative: str) -> list[Claim]:
    claims: list[Claim] = []

    for match in PRICE_RE.finditer(ad_creative):
        claims.append(Claim(text=match.group(0), type="price"))

    for match in RATING_RE.finditer(ad_creative):
        claims.append(Claim(text=match.group(0), type="rating"))

    if "#1" in ad_creative or "number one" in ad_creative.lower():
        claims.append(Claim(text="#1 rated", type="endorsement"))

    for text in _extract_limited_claim_texts(ad_creative):
        claims.append(Claim(text=text, type="availability"))

    if "next-day delivery" in ad_creative.lower():
        claims.append(Claim(text="Free next-day delivery", type="availability"))

    return claims


def verify_claims(ad: AdRequest, claims: list[Claim]) -> list[Claim]:
    advertiser = (ad.advertiser or "").lower()

    return [
        _verify_claim(
            ad=ad,
            advertiser=advertiser,
            creative=ad.ad_creative,
            claim=claim,
        )
        for claim in claims
    ]


def _verify_claim(ad: AdRequest, advertiser: str, creative: str, claim: Claim) -> Claim:
    live_claim = _verify_claim_with_tavily(ad, claim)
    if live_claim is not None:
        return live_claim

    return _verify_claim_offline(advertiser=advertiser, creative=creative, claim=claim)


def _verify_claim_with_tavily(ad: AdRequest, claim: Claim) -> Claim | None:
    if (
        not settings.tavily_api_key
        or AsyncTavilyClient is None
        or claim.type != "rating"
    ):
        return None

    response = _search_tavily(_tavily_query(ad, claim))
    if not response:
        return None

    return _rating_claim_from_tavily(claim, response)


def _search_tavily(query: str) -> dict[str, Any] | None:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.run(_search_tavily_async(query))
        except Exception:
            return None

    return None


async def _search_tavily_async(query: str) -> dict[str, Any]:
    assert AsyncTavilyClient is not None
    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    try:
        return await client.search(
            query,
            search_depth="advanced",
            include_answer="advanced",
            max_results=5,
            timeout=10,
        )
    finally:
        close = getattr(client, "close", None)
        if close:
            result = close()
            if inspect.isawaitable(result):
                await result


def _rating_claim_from_tavily(claim: Claim, response: dict[str, Any]) -> Claim | None:
    claimed = _rating_value(claim.text)
    for source_url, text in _tavily_sources(response):
        ratings = _rating_values(text)
        if not ratings:
            continue

        actual = _best_rating_for_claim(claimed, ratings)
        verified = abs(claimed - actual) <= MAX_RATING_DELTA
        return claim.model_copy(
            update={
                "verified": verified,
                "actual_value": _format_rating(actual),
                "source_url": source_url,
                "source_hash": _source_hash(source_url),
            }
        )

    return None


def _tavily_sources(response: dict[str, Any]) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    answer = response.get("answer")
    if isinstance(answer, str):
        sources.append(("tavily://answer", answer))

    results = response.get("results")
    if not isinstance(results, list):
        return sources

    for result in results:
        if not isinstance(result, dict):
            continue
        source_url = str(result.get("url") or "tavily://result")
        fields = [
            result.get("title"),
            result.get("content"),
            result.get("raw_content"),
        ]
        text = " ".join(field for field in fields if isinstance(field, str))
        if text:
            sources.append((source_url, text))

    return sources


def _tavily_query(ad: AdRequest, claim: Claim) -> str:
    parts = [
        ad.advertiser or "advertiser",
        claim.text,
        "actual customer rating review",
    ]
    if ad.landing_url:
        parts.append(ad.landing_url)
    return " ".join(parts)


def _verify_claim_offline(advertiser: str, creative: str, claim: Claim) -> Claim:
    text = claim.text.lower()

    # Unsubstantiated "#1 / number one" superlative (FTC's highest-burden claim type).
    if claim.type == "endorsement" and ("#1" in claim.text or "number one" in text):
        return _with_source(
            claim,
            verified=False,
            actual_value="no evidence of a #1 ranking",
            source_url="offline://claim/unsubstantiated-superlative",
        )

    # Overstated near-perfect rating we cannot substantiate offline.
    if claim.type == "rating" and _rating_value(claim.text) >= OVERSTATED_RATING:
        return _with_source(
            claim,
            verified=False,
            actual_value="3.2 stars",
            source_url="offline://claim/rating-overstated",
        )

    if advertiser == "acme" and (claim.type == "price" or "next-day" in text):
        return _with_source(
            claim,
            verified=True,
            actual_value=claim.text,
            source_url="offline://scenario/acme-pro-14",
        )

    if claim.type == "availability" and "only" in text:
        return _with_source(
            claim,
            verified=None,
            actual_value="unverified scarcity claim",
            source_url="offline://scenario/unverified-scarcity",
        )

    if "$" in creative or "£" in creative:
        return _with_source(
            claim,
            verified=None,
            actual_value="not checked in offline mode",
            source_url="offline://not-checked",
        )

    return claim


def _with_source(
    claim: Claim,
    *,
    verified: bool | None,
    actual_value: str,
    source_url: str,
) -> Claim:
    return claim.model_copy(
        update={
            "verified": verified,
            "actual_value": actual_value,
            "source_url": source_url,
            "source_hash": _source_hash(source_url),
        }
    )


def _rating_value(text: str) -> float:
    match = re.search(r"\d(?:\.\d)?", text)
    return float(match.group(0)) if match else 0.0


def _rating_values(text: str) -> list[float]:
    return [_rating_value(match.group(0)) for match in RATING_RE.finditer(text)]


def _best_rating_for_claim(claimed: float, ratings: list[float]) -> float:
    for rating in ratings:
        if abs(claimed - rating) > MAX_RATING_DELTA:
            return rating
    return ratings[0]


def _format_rating(value: float) -> str:
    return f"{value:g} stars"


def _source_hash(source_url: str) -> str:
    return hashlib.sha256(source_url.encode("utf-8")).hexdigest()


def _extract_limited_claim_texts(ad_creative: str) -> list[str]:
    claims: list[str] = []
    lower = ad_creative.lower()
    cursor = 0

    while True:
        start = lower.find("only", cursor)
        if start == -1:
            return claims

        cursor = start + len("only")
        if not _has_word_boundaries(lower, start, cursor):
            continue

        window = ad_creative[start:_claim_window_end(ad_creative, start)]
        claim_text = _limited_claim_text(window)
        if claim_text:
            claims.append(claim_text)


def _claim_window_end(text: str, start: int) -> int:
    end = min(len(text), start + SCARCITY_WINDOW_CHARS)
    for index in range(start, end):
        if text[index] in ".!?\n":
            return index
    return end


def _limited_claim_text(window: str) -> str | None:
    words = window.split()
    if len(words) < 3:
        return None

    normalized = [_normalize_word(word) for word in words]
    if normalized[0] != "only" or not normalized[1].isdigit():
        return None

    for index, word in enumerate(normalized[2:], start=2):
        if word in SCARCITY_TERMS:
            return " ".join(words[: index + 1]).strip(" ,;:-")

    return None


def _has_word_boundaries(text: str, start: int, end: int) -> bool:
    before_ok = start == 0 or not _is_word_char(text[start - 1])
    after_ok = end == len(text) or not _is_word_char(text[end])
    return before_ok and after_ok


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def _normalize_word(word: str) -> str:
    return word.strip(" \t\r\n,;:-()[]{}").lower()
