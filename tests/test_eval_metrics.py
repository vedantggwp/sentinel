"""Unit tests for the auxiliary eval metrics layer."""
from dataclasses import dataclass

from sentinel.eval_metrics import (
    classification_report,
    confusion_matrix,
    load_cost_matrix,
    weighted_cost,
)


@dataclass(frozen=True)
class Row:
    expected_verdict: str
    actual_verdict: str


def test_confusion_matrix_counts_each_cell():
    rows = [
        Row("BLOCK", "BLOCK"),
        Row("BLOCK", "APPROVE"),   # missed harm
        Row("APPROVE", "APPROVE"),
        Row("ESCALATE", "BLOCK"),
    ]
    m = confusion_matrix(rows)
    assert m["BLOCK"]["BLOCK"] == 1
    assert m["BLOCK"]["APPROVE"] == 1
    assert m["APPROVE"]["APPROVE"] == 1
    assert m["ESCALATE"]["BLOCK"] == 1


def test_classification_report_precision_recall():
    rows = [
        Row("BLOCK", "BLOCK"),
        Row("BLOCK", "BLOCK"),
        Row("BLOCK", "APPROVE"),   # a BLOCK we missed -> recall < 1
        Row("APPROVE", "BLOCK"),   # a wrong BLOCK    -> precision < 1
    ]
    report = classification_report(rows)
    assert report["BLOCK"]["recall"] == round(2 / 3, 4)      # 2 of 3 true BLOCKs caught
    assert report["BLOCK"]["precision"] == round(2 / 3, 4)   # 2 of 3 predicted BLOCKs correct
    assert report["BLOCK"]["support"] == 3


def test_cost_matrix_is_safety_first():
    matrix = load_cost_matrix()
    # Missing a BLOCK (harm placed) must be the single most expensive error,
    # and strictly costlier than wrongly blocking a clean ad (FN >> FP).
    assert matrix["BLOCK"]["APPROVE"] == max(
        matrix[truth][pred]
        for truth in matrix
        for pred in matrix[truth]
    )
    assert matrix["BLOCK"]["APPROVE"] > matrix["APPROVE"]["BLOCK"]
    # ESCALATE is the cheap human-review valve: over-escalating beats over-blocking.
    assert matrix["APPROVE"]["ESCALATE"] < matrix["APPROVE"]["BLOCK"]
    # Correct verdicts are free.
    assert all(matrix[v][v] == 0 for v in matrix)


def test_weighted_cost_aggregates_and_ranks_offenders():
    rows = [
        Row("BLOCK", "APPROVE"),   # cost 10
        Row("APPROVE", "BLOCK"),   # cost 2
        Row("APPROVE", "APPROVE"), # cost 0
    ]
    out = weighted_cost(rows)
    assert out["total_cost"] == 12
    assert out["n"] == 3
    assert out["worst"][0] == {"expected": "BLOCK", "actual": "APPROVE", "cost": 10}
