"""Phase 5 — L4 safety-judge calibration against a human gold set.

The L4 judge emits *numeric* dimension scores (it never decides — the gate
does). Numeric model-grades are known to be noisy/biased, so before trusting a
judge we measure how well its scores agree with human labels, per dimension,
using quadratic-weighted Cohen's kappa (the right statistic for an ordinal 1-5
scale). Target: kappa >= 0.6 per the 2026 LLM-as-judge bar.

JUDGE SEAM: a judge is any ``AdRequest -> {dimension: score}`` callable. The
default reads ``run_pipeline(ad).scores`` — i.e. whatever L4 the pipeline runs
*today* (currently the deterministic heuristic). When a real LLM judge replaces
the heuristic behind that seam, this harness calibrates it with zero changes.

Until an LLM judge is wired, this is a MEASUREMENT (how well the heuristic stub
tracks human judgement), not a hard gate — see tests/test_calibrate.py. The
gold set here is a bootstrap seed; the standard calls for >=200 traces with 2-3
annotators each, refreshed quarterly. Expand data/safety_gold.jsonl to that bar
before flipping ``main`` into a CI gate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping

from sentinel.contracts import AdRequest
from sentinel.eval_stats import cohens_kappa, pearson
from sentinel.pipeline import run_pipeline
from sentinel.pipeline.policy import load_policy

GOLD_PATH = Path(__file__).resolve().parents[1] / "data" / "safety_gold.jsonl"
KAPPA_TARGET = 0.6  # LLM-as-judge agreement bar (2026)
SCORE_MIN, SCORE_MAX = 1, 5

JudgeFn = Callable[[AdRequest], Mapping[str, float]]


def pipeline_judge(ad: AdRequest) -> Mapping[str, float]:
    """Default judge: the L4 scores the current pipeline produces today."""
    return run_pipeline(ad).scores


def bucket(score: float) -> int:
    """Snap a continuous score to the integer 1-5 scale humans labelled on."""
    return max(SCORE_MIN, min(SCORE_MAX, round(score)))


def load_gold(path: Path | None = None) -> list[dict]:
    """Read JSONL gold cases, skipping any leading ``_meta`` provenance line."""
    lines = (path or GOLD_PATH).read_text(encoding="utf-8").splitlines()
    cases = [json.loads(line) for line in lines if line.strip()]
    return [c for c in cases if "_meta" not in c]


def _dimensions() -> list[str]:
    return list(load_policy().get("dimensions", []))


def calibrate(
    gold: list[dict] | None = None,
    *,
    judge: JudgeFn = pipeline_judge,
    target: float = KAPPA_TARGET,
) -> dict:
    """Per-dimension weighted kappa (judge vs human) plus a length-bias probe."""
    cases = gold if gold is not None else load_gold()
    dimensions = _dimensions()

    predicted = [judge(_to_request(case, index)) for index, case in enumerate(cases)]
    categories = list(range(SCORE_MIN, SCORE_MAX + 1))

    per_dimension: dict[str, dict] = {}
    for dim in dimensions:
        pairs = [
            (bucket(pred[dim]), int(case["labels"][dim]))
            for case, pred in zip(cases, predicted)
            if dim in case.get("labels", {}) and dim in pred
        ]
        if not pairs:
            continue
        judged, human = [p for p, _ in pairs], [h for _, h in pairs]
        kappa = cohens_kappa(judged, human, categories=categories, weights="quadratic")
        per_dimension[dim] = {
            "kappa": round(kappa, 4),
            "n": len(pairs),
            "target_met": kappa >= target,
        }

    kappas = [d["kappa"] for d in per_dimension.values()]
    overall = round(sum(kappas) / len(kappas), 4) if kappas else 0.0
    return {
        "n_cases": len(cases),
        "annotator_floor_met": all(c.get("annotators", 0) >= 2 for c in cases),
        "target_kappa": target,
        "per_dimension": per_dimension,
        "overall_kappa": overall,
        "overall_target_met": overall >= target,
        "length_bias": _length_bias(cases, predicted, dimensions),
    }


def _length_bias(cases: list[dict], predicted: list[Mapping[str, float]], dimensions: list[str]) -> dict:
    """Correlate creative length with the judge's mean score.

    A judge that scores longer copy systematically higher/lower is length-biased;
    |r| near 0 is the healthy result. (Position / family / self-enhancement biases
    attach at the JudgeFn seam once an LLM judge replaces the heuristic — they
    cannot manifest in a deterministic scorer, so no dead probe is written here.)
    """
    lengths = [float(len(c["input"]["ad_creative"])) for c in cases]
    means = [
        sum(pred[d] for d in dimensions if d in pred) / max(1, sum(d in pred for d in dimensions))
        for pred in predicted
    ]
    return {"length_vs_score_r": round(pearson(lengths, means), 4)}


def _to_request(case: dict, index: int) -> AdRequest:
    payload = case["input"]
    return AdRequest(
        ad_id=case.get("ad_id", f"gold-{index}"),
        conversation=payload["conversation"],
        ad_creative=payload["ad_creative"],
        advertiser=payload.get("advertiser"),
    )


def main() -> int:
    report = calibrate()
    print(json.dumps(report, indent=2))
    # Not yet a hard gate: no LLM judge is wired and the gold set is a seed.
    # Returns 0 always; flip to `0 if report["overall_target_met"] else 1` once
    # an LLM judge lands and the gold set reaches the 200/2-3-annotator bar.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
