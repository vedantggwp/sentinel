from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sentinel.contracts import AdRequest
from sentinel.eval_metrics import classification_report, confusion_matrix, weighted_cost
from sentinel.eval_stats import wilson_interval
from sentinel.pipeline import run_pipeline

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_CASES_PATH = DATA_DIR / "overmind_seed_cases.json"
ADVERSARIAL_CASES_PATH = DATA_DIR / "adversarial_cases.json"


@dataclass(frozen=True)
class EvalCaseResult:
    index: int
    expected_verdict: str
    actual_verdict: str
    expected_rule_fired: str | None
    actual_rule_fired: str
    passed: bool
    reason: str


def load_cases(path: Path | None = None) -> list[dict]:
    case_path = path or DEFAULT_CASES_PATH
    return json.loads(case_path.read_text(encoding="utf-8"))


def run_case(case: dict, *, index: int, ad_id: str | None = None) -> EvalCaseResult:
    payload = case["input"]
    ad = AdRequest(
        ad_id=ad_id or f"eval-{index}",
        conversation=payload["conversation"],
        ad_creative=payload["ad_creative"],
        advertiser=payload.get("advertiser"),
    )
    result = run_pipeline(ad)
    expected_verdict = case["expected_output"]
    actual_verdict = result.verdict.value
    expected_rule = case.get("expected_rule_fired")
    verdict_ok = actual_verdict == expected_verdict
    rule_ok = expected_rule is None or result.rule_fired == expected_rule
    return EvalCaseResult(
        index=index,
        expected_verdict=expected_verdict,
        actual_verdict=actual_verdict,
        expected_rule_fired=expected_rule,
        actual_rule_fired=result.rule_fired,
        passed=verdict_ok and rule_ok,
        reason=result.reason,
    )


def run_all(cases: list[dict] | None = None, *, path: Path | None = None) -> list[EvalCaseResult]:
    rows = cases if cases is not None else load_cases(path)
    return [run_case(case, index=index) for index, case in enumerate(rows)]


def summarize(results: list[EvalCaseResult]) -> dict:
    """Binary pass/fail (the primary scorer) plus auxiliary metrics.

    Headline accuracy is reported with a 95% Wilson confidence interval rather
    than as a bare count — a single pass rate over n=25 hides real uncertainty.
    """
    total = len(results)
    failed = [row for row in results if not row.passed]
    passed = total - len(failed)
    ci_low, ci_high = wilson_interval(passed, total)
    return {
        "total": total,
        "passed": passed,
        "failed": len(failed),
        "accuracy": round(passed / total, 4) if total else 0.0,
        "accuracy_ci95": [round(ci_low, 4), round(ci_high, 4)],
        "confusion_matrix": confusion_matrix(results),
        "classification_report": classification_report(results),
        "cost": weighted_cost(results),
        "failures": [
            {
                "index": row.index,
                "expected_verdict": row.expected_verdict,
                "actual_verdict": row.actual_verdict,
                "expected_rule_fired": row.expected_rule_fired,
                "actual_rule_fired": row.actual_rule_fired,
                "reason": row.reason,
            }
            for row in failed
        ],
    }


def main() -> int:
    """Run the regression (seed) split and, if present, the adversarial split.

    Exit status gates on the seed split only — the adversarial split is a
    held-out *measurement* of how brittle the heuristics are, not a pass/fail
    gate (many of its cases are written to fail on purpose).
    """
    seed = summarize(run_all())
    print("# seed (regression gate)")
    print(json.dumps(seed, indent=2))

    if ADVERSARIAL_CASES_PATH.exists():
        adversarial = summarize(run_all(load_cases(ADVERSARIAL_CASES_PATH)))
        print("\n# adversarial / held-out (measurement only — not gated)")
        print(json.dumps(adversarial, indent=2))

    return 0 if seed["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
