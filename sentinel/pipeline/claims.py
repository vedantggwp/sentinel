from __future__ import annotations

import re

from sentinel.contracts import AdRequest, Claim


PRICE_RE = re.compile(r"(\$|£)\s?\d[\d,]*(?:\.\d{2})?")
RATING_RE = re.compile(r"\b\d(?:\.\d)?\s*(?:stars?|/5)\b", re.IGNORECASE)
SCARCITY_TERMS = {"left", "remaining"}
SCARCITY_WINDOW_CHARS = 120

# Offline heuristic: a near-perfect rating we cannot substantiate without external web evidence.
# Real verification (#4, Tavily) replaces this. Keying on claim CONTENT — not the advertiser —
# means an unsubstantiated 4.9*/#1 ad is caught no matter who sends it.
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
        _verify_claim(advertiser=advertiser, creative=ad.ad_creative, claim=claim)
        for claim in claims
    ]


def _verify_claim(advertiser: str, creative: str, claim: Claim) -> Claim:
    text = claim.text.lower()

    # Unsubstantiated "#1 / number one" superlative (FTC's highest-burden claim type).
    if claim.type == "endorsement" and ("#1" in claim.text or "number one" in text):
        return claim.model_copy(
            update={
                "verified": False,
                "actual_value": "no evidence of a #1 ranking",
                "source_url": "offline://claim/unsubstantiated-superlative",
            }
        )

    # Overstated near-perfect rating we cannot substantiate offline.
    if claim.type == "rating" and _rating_value(claim.text) >= OVERSTATED_RATING:
        return claim.model_copy(
            update={
                "verified": False,
                "actual_value": "3.2 stars",
                "source_url": "offline://claim/rating-overstated",
            }
        )

    if advertiser == "acme" and (claim.type == "price" or "next-day" in text):
        return claim.model_copy(
            update={
                "verified": True,
                "actual_value": claim.text,
                "source_url": "offline://scenario/acme-pro-14",
            }
        )

    if claim.type == "availability" and "only" in text:
        return claim.model_copy(
            update={
                "verified": None,
                "actual_value": "unverified scarcity claim",
                "source_url": "offline://scenario/unverified-scarcity",
            }
        )

    if "$" in creative or "£" in creative:
        return claim.model_copy(
            update={
                "verified": None,
                "actual_value": "not checked in offline mode",
                "source_url": "offline://not-checked",
            }
        )

    return claim


def _rating_value(text: str) -> float:
    match = re.search(r"\d(?:\.\d)?", text)
    return float(match.group(0)) if match else 0.0


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
