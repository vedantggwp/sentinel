"""Held-out adversarial split — a measurement, not a regression gate.

These cases were written to probe blind spots the seed set never exercises
(negation, paraphrase, obfuscation, benign trigger words, implied-minor,
homoglyphs). Each row carries the CORRECT verdict plus ``currently_passes``
documenting today's heuristic behaviour. The test pins that snapshot, so when
the pipeline genuinely improves a case the snapshot breaks LOUDLY and forces
the doc to be updated (and celebrated).
"""
import json
from pathlib import Path

import pytest

from sentinel.eval import run_all, summarize

CASES_PATH = Path(__file__).resolve().parents[1] / "data" / "adversarial_cases.json"
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))
RESULTS = run_all(CASES)


@pytest.mark.parametrize("index", range(len(CASES)))
def test_adversarial_snapshot(index):
    case = CASES[index]
    row = RESULTS[index]
    assert row.passed == case["currently_passes"], (
        f"case {index} changed behaviour: expected snapshot "
        f"currently_passes={case['currently_passes']} but pipeline now "
        f"{'passes' if row.passed else 'fails'} "
        f"(verdict={row.actual_verdict}, rule={row.actual_rule_fired}). "
        f"Update data/adversarial_cases.json if this is an intended improvement."
    )


def test_split_contains_real_failures():
    # If every adversarial case passes, the split has stopped being adversarial.
    failing = [c for c, r in zip(CASES, RESULTS) if not r.passed]
    assert failing, "adversarial split has no failing cases — it is no longer held-out"


def test_held_out_accuracy_is_below_fitted():
    # The whole point: fitted accuracy hides brittleness the held-out split exposes.
    from sentinel.eval import load_cases

    seed = summarize(run_all(load_cases()))
    adversarial = summarize(RESULTS)
    assert adversarial["accuracy"] < seed["accuracy"], (
        f"held-out accuracy {adversarial['accuracy']} should trail fitted "
        f"{seed['accuracy']} — if not, the split is no longer adversarial"
    )
