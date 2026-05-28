from __future__ import annotations

import re

from sentinel.contracts import AdRequest, Claim


PRICE_RE = re.compile(r"(\$|£)\s?\d[\d,]*(?:\.\d{2})?")
RATING_RE = re.compile(r"\b\d(?:\.\d)?\s*(?:stars?|/5)\b", re.IGNORECASE)
LIMITED_RE = re.compile(r"\bonly\s+\d+\s+[^.!?]+(?:left|remaining)\b", re.IGNORECASE)


def extract_claims(ad_creative: str) -> list[Claim]:
    claims: list[Claim] = []

    for match in PRICE_RE.finditer(ad_creative):
        claims.append(Claim(text=match.group(0), type="price"))

    for match in RATING_RE.finditer(ad_creative):
        claims.append(Claim(text=match.group(0), type="rating"))

    if "#1" in ad_creative or "number one" in ad_creative.lower():
        claims.append(Claim(text="#1 rated", type="endorsement"))

    for match in LIMITED_RE.finditer(ad_creative):
        claims.append(Claim(text=match.group(0), type="availability"))

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

    if advertiser == "sonicmax" and claim.type in {"rating", "endorsement"}:
        return claim.model_copy(
            update={
                "verified": False,
                "actual_value": "3.2 stars",
                "source_url": "offline://scenario/sonicmax-rating",
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
