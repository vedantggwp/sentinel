"""Unit tests for the pure-stdlib eval statistics, pinned to reference values."""
import math

from sentinel.eval_stats import mcnemar_exact, wilson_interval


# --- Wilson interval (plain) ------------------------------------------------

def test_wilson_matches_published_reference():
    # n=10, x=5, 95% -> [0.2366, 0.7634] (standard reference value).
    low, high = wilson_interval(5, 10)
    assert math.isclose(low, 0.2366, abs_tol=1e-3)
    assert math.isclose(high, 0.7634, abs_tol=1e-3)


def test_wilson_perfect_score_stays_in_unit_interval():
    # 25/25 must NOT report [1.0, 1.0]; the lower bound carries the uncertainty.
    low, high = wilson_interval(25, 25)
    assert high == 1.0
    assert 0.80 < low < 1.0  # ~0.866 — a perfect run on n=25 is still uncertain


def test_wilson_zero_and_empty_are_safe():
    assert wilson_interval(0, 10)[0] == 0.0
    assert wilson_interval(0, 0) == (0.0, 0.0)


# --- Wilson interval (continuity-corrected) ---------------------------------

def test_continuity_correction_is_wider_and_bounded():
    plain = wilson_interval(5, 10)
    cc = wilson_interval(5, 10, continuity=True)
    assert cc[0] <= plain[0] and cc[1] >= plain[1]
    assert math.isclose(cc[0], 0.2014, abs_tol=5e-3)
    assert math.isclose(cc[1], 0.7986, abs_tol=5e-3)
    assert 0.0 <= cc[0] <= cc[1] <= 1.0


# --- McNemar exact ----------------------------------------------------------

def test_mcnemar_exact_reference_value():
    # b=10, c=2 -> exact two-sided p ~= 0.0386.
    assert math.isclose(mcnemar_exact(10, 2), 0.03857, abs_tol=1e-4)


def test_mcnemar_no_disagreement_is_one():
    assert mcnemar_exact(0, 0) == 1.0


def test_mcnemar_symmetric_disagreement_not_significant():
    assert mcnemar_exact(5, 5) == 1.0
