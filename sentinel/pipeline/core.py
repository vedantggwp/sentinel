from __future__ import annotations

from sentinel.contracts import AdRequest, PipelineResult
from sentinel.pipeline.claim_extractor import extract_claims
from sentinel.pipeline.context_gate import assess_context_with_evidence
from sentinel.pipeline.fact_verifier import verify_claims
from sentinel.pipeline.gate import decide_placement
from sentinel.pipeline.policy import load_policy
from sentinel.pipeline.safety_judge import score_safety


def run_pipeline(ad: AdRequest) -> PipelineResult:
    context = assess_context_with_evidence(ad.conversation)
    claims = verify_claims(ad, extract_claims(ad.ad_creative))
    scores = score_safety(
        ad_creative=ad.ad_creative,
        contextual_safety=context.contextual_safety,
        claims=claims,
    )
    scores.update(context.scores)
    verdict, rule_fired, reason = decide_placement(
        scores=scores,
        vulnerability_flags=context.vulnerability_flags,
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
        vulnerability_flags=context.vulnerability_flags,
    )
