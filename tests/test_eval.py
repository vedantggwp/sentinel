"""Regression evals for the full pipeline against seed cases."""
import json
from pathlib import Path

import pytest

from sentinel.eval import load_cases, run_all, summarize

CASES_PATH = Path(__file__).resolve().parents[1] / "data" / "overmind_seed_cases.json"
CASES = load_cases(CASES_PATH)


def test_eval_dataset_has_twenty_five_cases():
    assert len(CASES) == 25


def test_eval_dataset_matches_overmind_shape():
    for case in CASES:
        assert "input" in case
        assert "conversation" in case["input"]
        assert "ad_creative" in case["input"]
        assert case["expected_output"] in {"APPROVE", "BLOCK", "ESCALATE"}


@pytest.mark.parametrize("index", range(len(CASES)))
def test_seed_case(index: int):
    case = CASES[index]
    results = run_all([case])
    row = results[0]
    assert row.actual_verdict == case["expected_output"], (
        f"case {index}: expected {case['expected_output']} got {row.actual_verdict} "
        f"(rule={row.actual_rule_fired}, reason={row.reason})"
    )
    if "expected_rule_fired" in case:
        assert row.actual_rule_fired == case["expected_rule_fired"], (
            f"case {index}: expected rule {case['expected_rule_fired']} "
            f"got {row.actual_rule_fired}"
        )


def test_all_seed_cases_pass():
    report = summarize(run_all(CASES))
    assert report["failed"] == 0, json.dumps(report["failures"], indent=2)
