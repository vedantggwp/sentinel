from __future__ import annotations

from sentinel.contracts import AdRequest, PipelineResult
from sentinel.pipeline.claim_extractor import extract_claims
from sentinel.pipeline.context_gate import assess_context
from sentinel.pipeline.fact_verifier import verify_claims
from sentinel.pipeline.gate import decide_placement
from sentinel.pipeline.policy import load_policy
from sentinel.pipeline.safety_judge import score_safety


def run_pipeline(ad: AdRequest) -> PipelineResult:
    vulnerability_flags, contextual_safety = assess_context(ad.conversation)
    claims = verify_claims(ad, extract_claims(ad.ad_creative))
    scores = score_safety(
        ad_creative=ad.ad_creative,
        contextual_safety=contextual_safety,
        claims=claims,
    )
    verdict, rule_fired, reason = decide_placement(
        scores=scores,
        vulnerability_flags=vulnerability_flags,
        claims=claims,
        policy=load_policy(),
    )

    return PipelineResult(
        ad_id=ad.ad_id,
        verdict=verdict,
        scores=scores,
        claims=claims,
        reason=reason,
        rule_fired=rule_fired,
        vulnerability_flags=vulnerability_flags,
    )
