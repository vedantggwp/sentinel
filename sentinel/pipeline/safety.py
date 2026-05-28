from __future__ import annotations

from sentinel.contracts import Claim


URGENCY_PATTERNS = (
    "last chance",
    "only ",
    "limited time",
    "act now",
    "hurry",
    "!!!",
)

TONE_MIMICRY_PATTERNS = (
    "as your assistant",
    "i recommend",
    "because you told me",
)

GREY_ZONE_TONE_PATTERNS = (
    "recommended for you",
    "selected for your conversation",
    "based on this conversation",
)


def score_safety(
    ad_creative: str,
    contextual_safety: float,
    claims: list[Claim],
) -> dict[str, float]:
    text = ad_creative.lower()

    return {
        "contextual_safety": contextual_safety,
        "claim_truthfulness": _score_claim_truthfulness(claims),
        "urgency_manipulation": _score_urgency(text),
        "tone_mimicry": _score_tone_mimicry(text),
    }


def _score_claim_truthfulness(claims: list[Claim]) -> float:
    if any(claim.verified is False for claim in claims):
        return 1.0
    if any(claim.verified is None for claim in claims):
        return 4.0
    return 5.0


def _score_urgency(text: str) -> float:
    return 1.0 if any(pattern in text for pattern in URGENCY_PATTERNS) else 5.0


def _score_tone_mimicry(text: str) -> float:
    if any(pattern in text for pattern in TONE_MIMICRY_PATTERNS):
        return 2.0
    if any(pattern in text for pattern in GREY_ZONE_TONE_PATTERNS):
        return 3.0
    return 5.0
