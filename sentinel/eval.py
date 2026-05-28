from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sentinel.contracts import AdRequest
from sentinel.pipeline import run_pipeline

DEFAULT_CASES_PATH = Path(__file__).resolve().parents[1] / "data" / "overmind_seed_cases.json"


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
    failed = [row for row in results if not row.passed]
    return {
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
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
    results = run_all()
    report = summarize(results)
    print(json.dumps(report, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
