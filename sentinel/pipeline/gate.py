from __future__ import annotations

from sentinel.contracts import Claim, Verdict


def decide_placement(
    scores: dict[str, float],
    vulnerability_flags: list[str],
    claims: list[Claim],
    policy: dict | None = None,
) -> tuple[Verdict, str, str]:
    if vulnerability_flags:
        return (
            Verdict.BLOCK,
            "vulnerability_auto_block",
            "Ineligible conversation context: " + ", ".join(vulnerability_flags),
        )

    false_claims = [claim for claim in claims if claim.verified is False]
    if false_claims:
        claim = false_claims[0]
        detail = claim.actual_value or claim.text
        return Verdict.BLOCK, "false_claim", "Claim failed verification: " + detail

    dimensions = _dimensions(policy, scores)
    if not dimensions or any(dimension not in scores for dimension in dimensions):
        return Verdict.ESCALATE, "missing_scores", "Missing one or more policy scores"

    overall = min(scores[dimension] for dimension in dimensions)
    block_threshold = (policy or {}).get("block_if_overall_below", 3.0)
    if overall < block_threshold:
        if _only_urgency_fails(scores, dimensions, block_threshold):
            return Verdict.BLOCK, "urgency_manipulation", "Ad uses manipulative urgency"
        return Verdict.BLOCK, "low_overall_score", "Overall safety score is below the block threshold"

    low, high = (policy or {}).get("escalate_band", [2.5, 3.5])
    if low <= overall <= high:
        return Verdict.ESCALATE, "grey_zone", "Safety score is in the review band"

    return Verdict.APPROVE, "passed", "All deterministic gate checks passed"


def _dimensions(policy: dict | None, scores: dict[str, float]) -> list[str]:
    if policy and "dimensions" in policy:
        return list(policy["dimensions"])
    return list(scores)


def _only_urgency_fails(
    scores: dict[str, float],
    dimensions: list[str],
    threshold: float,
) -> bool:
    if scores.get("urgency_manipulation", threshold) >= threshold:
        return False
    return all(
        scores[dimension] >= threshold
        for dimension in dimensions
        if dimension != "urgency_manipulation"
    )
