from __future__ import annotations

import re
import unicodedata

from sentinel.contracts import Claim


URGENCY_PATTERNS = (
    "last chance",
    "only ",
    "limited time",
    "act now",
    "hurry",
    "!!!",
)

SCARCITY_PARAPHRASES = (
    "running low",
    "before they're gone",
    "before they are gone",
    "while supplies last",
    "ends tonight",
)

NEGATED_URGENCY_PATTERNS = (
    "not your last chance",
    "not the last chance",
    "not last chance",
)

HOMOGLYPHS = str.maketrans(
    {
        "а": "a",  # Cyrillic small a
        "А": "a",
        "е": "e",
        "Е": "e",
        "о": "o",
        "О": "o",
        "с": "c",
        "С": "c",
        "р": "p",
        "Р": "p",
        "х": "x",
        "Х": "x",
        "у": "y",
        "У": "y",
    }
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
    text = _normalize_text(ad_creative)

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
    text = _remove_negated_urgency(text)
    compact = re.sub(r"[^a-z0-9]+", "", text)
    if "lastchance" in compact:
        return 1.0
    if any(pattern in text for pattern in URGENCY_PATTERNS):
        return 1.0
    if any(pattern in text for pattern in SCARCITY_PARAPHRASES):
        return 1.0
    return 5.0


def _score_tone_mimicry(text: str) -> float:
    if any(pattern in text for pattern in TONE_MIMICRY_PATTERNS):
        return 2.0
    if any(pattern in text for pattern in GREY_ZONE_TONE_PATTERNS):
        return 3.0
    return 5.0


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).translate(HOMOGLYPHS).lower()
    return re.sub(r"\s+", " ", normalized)


def _remove_negated_urgency(text: str) -> str:
    without_negations = text
    for pattern in NEGATED_URGENCY_PATTERNS:
        without_negations = without_negations.replace(pattern, "")
    return without_negations
