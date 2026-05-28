"""Robustness of the deterministic gate to score jitter near its thresholds.

The L4 judge emits *numeric* scores, and numeric model-grades are known to be
noisy/biased (per the AISI standard). The gate is deterministic, so it faithfully
propagates that noise — these tests prove a small wobble can only ever move the
verdict to an ADJACENT band (BLOCK<->ESCALATE<->APPROVE), never silently jump
BLOCK<->APPROVE, and that the band boundaries sit exactly where policy says.
"""
import json
from pathlib import Path

from sentinel.contracts import Verdict
from sentinel.pipeline.gate import decide_placement

POLICY = json.loads((Path(__file__).resolve().parents[1] / "data" / "policy.json").read_text())
DIMENSIONS = POLICY["dimensions"]
RANK = {Verdict.BLOCK: 0, Verdict.ESCALATE: 1, Verdict.APPROVE: 2}


def verdict_for_overall(overall: float) -> Verdict:
    # All dimensions equal => overall == min == this value, no single-dimension
    # special-case, so we isolate the pure score->band mapping.
    scores = {d: overall for d in DIMENSIONS}
    return decide_placement(scores, [], [], POLICY)[0]


def test_no_single_step_skips_a_band():
    # Sweep the overall score in fine steps; the verdict rank must be monotonic
    # non-decreasing and never jump by more than one band per 0.05 step.
    values = [round(0.05 * i, 2) for i in range(0, 101)]  # 0.00 .. 5.00
    ranks = [RANK[verdict_for_overall(v)] for v in values]
    assert ranks == sorted(ranks), "verdict is not monotonic in the safety score"
    assert all(abs(b - a) <= 1 for a, b in zip(ranks, ranks[1:])), "a 0.05 jitter skipped a band"


def test_band_boundaries_match_policy():
    # block_if_overall_below=3.0; escalate_band=[2.5, 3.5] (block check runs first).
    assert verdict_for_overall(2.95) is Verdict.BLOCK
    assert verdict_for_overall(3.00) is Verdict.ESCALATE
    assert verdict_for_overall(3.50) is Verdict.ESCALATE
    assert verdict_for_overall(3.55) is Verdict.APPROVE


def test_jitter_around_block_threshold_never_reaches_approve():
    # +/-0.1 around the 3.0 block line can reach ESCALATE but never APPROVE.
    for v in (2.9, 2.95, 3.0, 3.05, 3.1):
        assert verdict_for_overall(v) is not Verdict.APPROVE


def test_urgency_only_failure_is_robust_in_its_band():
    # A lone failing urgency dimension blocks; a 0.1 wobble below threshold keeps it blocking.
    for u in (1.0, 2.0, 2.9):
        scores = {d: 5.0 for d in DIMENSIONS} | {"urgency_manipulation": u}
        verdict, rule, _ = decide_placement(scores, [], [], POLICY)
        assert verdict is Verdict.BLOCK
        assert rule == "urgency_manipulation"
