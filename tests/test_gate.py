"""Exhaustive tests for the deterministic gate.

The gate is the only component that DECIDES. These tests pin every branch and,
critically, prove the LLM can never override it:
  - `decide_placement` has no `verdict` parameter (structural guarantee).
  - a vulnerability flag blocks even with perfect scores + truthful claims.
"""
import inspect
import json
from pathlib import Path

from sentinel.contracts import Claim, Verdict
from sentinel.pipeline.gate import decide_placement

POLICY = json.loads((Path(__file__).resolve().parents[1] / "data" / "policy.json").read_text())

SAFE_SCORES = {d: 5.0 for d in POLICY["dimensions"]}
MID_SCORES = {d: 3.0 for d in POLICY["dimensions"]}  # inside escalate band [2.5, 3.5)
LOW_SCORES = {d: 1.0 for d in POLICY["dimensions"]}


def decide(scores, flags=None, claims=None):
    return decide_placement(scores, flags or [], claims or [], POLICY)


# --- Hard rule: vulnerability auto-block, no override -----------------------

def test_vulnerability_flag_blocks_even_with_perfect_scores():
    verdict, rule, _ = decide(SAFE_SCORES, flags=["financial_distress"])
    assert verdict is Verdict.BLOCK
    assert rule == "vulnerability_auto_block"


def test_vulnerability_blocks_even_with_truthful_claims():
    truthful = [Claim(text="$999", type="price", verified=True)]
    verdict, rule, _ = decide(SAFE_SCORES, flags=["minor"], claims=truthful)
    assert verdict is Verdict.BLOCK
    assert rule == "vulnerability_auto_block"


# --- Hard rule: a proven-false claim blocks ---------------------------------

def test_false_claim_blocks():
    claims = [Claim(text="4.9 stars on Amazon", type="rating", verified=False,
                    actual_value="3.2")]
    verdict, rule, reason = decide(SAFE_SCORES, claims=claims)
    assert verdict is Verdict.BLOCK
    assert rule == "false_claim"
    assert "3.2" in reason  # actual value surfaced for the receipt


def test_unverified_none_claim_does_not_block():
    # verified=None means "not checked", not "false" — must not trigger the block.
    claims = [Claim(text="great laptop", type="statistic", verified=None)]
    verdict, _, _ = decide(SAFE_SCORES, claims=claims)
    assert verdict is Verdict.APPROVE


# --- Score-based three-way decision -----------------------------------------

def test_high_scores_approve():
    verdict, rule, _ = decide(SAFE_SCORES)
    assert verdict is Verdict.APPROVE
    assert rule == "passed"


def test_mid_scores_escalate():
    verdict, rule, _ = decide(MID_SCORES)
    assert verdict is Verdict.ESCALATE
    assert rule == "grey_zone"


def test_low_scores_block():
    verdict, rule, _ = decide(LOW_SCORES)
    assert verdict is Verdict.BLOCK
    assert rule == "low_overall_score"


def test_missing_scores_escalate_to_human():
    verdict, rule, _ = decide({})
    assert verdict is Verdict.ESCALATE
    assert rule == "missing_scores"


# --- Precedence: hard rules beat scores -------------------------------------

def test_vulnerability_beats_low_scores_rule_name():
    # Both a flag and low scores apply; the vulnerability rule must win.
    verdict, rule, _ = decide(LOW_SCORES, flags=["self_harm"])
    assert verdict is Verdict.BLOCK
    assert rule == "vulnerability_auto_block"


# --- Structural guarantee: the gate cannot read an LLM verdict --------------

def test_gate_signature_has_no_verdict_input():
    params = set(inspect.signature(decide_placement).parameters)
    assert "verdict" not in params
    assert params == {"scores", "vulnerability_flags", "claims", "policy"}
