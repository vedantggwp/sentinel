from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sentinel.config import settings
from sentinel.contracts import AdRequest, Attestation, PipelineResult

AUDIT_PATH = Path("data/audit/decisions.jsonl")


def record_decision(
    ad: AdRequest,
    result: PipelineResult,
    attestation: Attestation,
) -> dict:
    record = _audit_record(ad, result, attestation)
    _write_record(record)
    _emit_overmind_span(record)
    return record


def latest_decisions(limit: int = 20) -> list[dict]:
    if not AUDIT_PATH.exists():
        return []

    rows = AUDIT_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(row) for row in rows[-limit:]]


def _audit_record(
    ad: AdRequest,
    result: PipelineResult,
    attestation: Attestation,
) -> dict:
    return {
        "trace_id": str(uuid4()),
        "issued_at": datetime.now(UTC).isoformat(),
        "ad_id": ad.ad_id,
        "advertiser": ad.advertiser,
        "input_hash": _hash_json(ad.model_dump(mode="json")),
        "ad_hash": attestation.ad_hash,
        "verdict": result.verdict.value,
        "rule_fired": result.rule_fired,
        "reason": result.reason,
        "scores": result.scores,
        "vulnerability_flags": result.vulnerability_flags,
        "models_used": attestation.models_used,
        "claims": [
            {
                "text": claim.text,
                "type": claim.type,
                "verified": claim.verified,
                "actual_value": claim.actual_value,
                "source_url": claim.source_url,
                "source_hash": _hash_text(claim.source_url or ""),
            }
            for claim in result.claims
        ],
        "attestation_hash": _hash_json(attestation.model_dump(mode="json")),
    }


def _write_record(record: dict) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def _emit_overmind_span(record: dict) -> None:
    if not settings.overmind_api_key:
        return

    try:
        import overmind

        overmind.init(
            settings.overmind_api_key,
            service_name=settings.overmind_service_name,
            environment=settings.overmind_environment,
        )
        tracer = overmind.get_tracer()
        with tracer.start_as_current_span("sentinel.decision") as span:
            span.set_attribute("sentinel.ad_id", record["ad_id"])
            span.set_attribute("sentinel.verdict", record["verdict"])
            span.set_attribute("sentinel.rule_fired", record["rule_fired"])
    except Exception:
        return


def _hash_json(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return _hash_text(payload)


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
