"""Tests for the Phase 5 L4 judge calibration harness."""
from sentinel.calibrate import (
    GOLD_PATH,
    KAPPA_TARGET,
    bucket,
    calibrate,
    load_gold,
    pipeline_judge,
)

GOLD = load_gold()
DIMS = ("contextual_safety", "claim_truthfulness", "urgency_manipulation", "tone_mimicry")


def _perfect_judge(ad):
    # Echo the human labels for this case -> the judge that agrees perfectly.
    labels = {c["ad_id"]: c["labels"] for c in GOLD}[ad.ad_id]
    return {dim: float(v) for dim, v in labels.items()}


def _always_safe_judge(ad):
    # Scores everything maximally safe -> wrong on every vulnerable/manipulative case.
    return {dim: 5.0 for dim in DIMS}


# --- gold loading -----------------------------------------------------------

def test_load_gold_skips_meta_line():
    assert GOLD, "gold set should have cases"
    assert all("labels" in c and "input" in c for c in GOLD)
    assert all("_meta" not in c for c in GOLD)


def test_bucket_clamps_to_scale():
    assert bucket(0.0) == 1
    assert bucket(2.4) == 2
    assert bucket(9.9) == 5


# --- the harness reports per-dimension kappa --------------------------------

def test_calibrate_reports_every_dimension():
    report = calibrate(GOLD)
    for dim in DIMS:
        assert dim in report["per_dimension"]
        assert report["per_dimension"][dim]["n"] == len(GOLD)
        assert -1.0 <= report["per_dimension"][dim]["kappa"] <= 1.0
    assert -1.0 <= report["length_bias"]["length_vs_score_r"] <= 1.0


def test_seed_set_is_honestly_below_the_annotator_bar():
    # The bootstrap seed must not masquerade as a 2-3 annotator gold set.
    assert calibrate(GOLD)["annotator_floor_met"] is False


# --- judge seam: detects good and bad judges --------------------------------

def test_perfect_judge_scores_kappa_one():
    report = calibrate(GOLD, judge=_perfect_judge)
    assert report["overall_kappa"] == 1.0
    assert report["overall_target_met"] is True


def test_miscalibrated_judge_is_caught():
    # An "everything is safe" judge must fail the agreement bar -> harness works.
    report = calibrate(GOLD, judge=_always_safe_judge)
    assert report["overall_kappa"] < KAPPA_TARGET
    assert report["overall_target_met"] is False


# --- characterization of today's heuristic judge ----------------------------

def test_current_heuristic_judge_meets_target_on_seed():
    # Snapshot: the deterministic L4 stub already tracks the seed gold well.
    # When an LLM judge replaces it, update this expectation deliberately.
    report = calibrate(GOLD, judge=pipeline_judge)
    assert report["overall_target_met"] is True
    assert GOLD_PATH.exists()
