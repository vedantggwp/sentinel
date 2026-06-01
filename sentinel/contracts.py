"""Shared interface contracts — the handshake between pipeline, integrations, and UI.

Import these; do NOT edit unless you own this file. Every module depends on these
shapes, so a change here needs a quick sync first.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"  # grey-zone -> human review


class AdRequest(BaseModel):
    """A candidate ad plus the conversation it would appear in."""

    ad_id: str
    conversation: str  # recent user/assistant turns
    ad_creative: str  # the ad copy / claims
    advertiser: str | None = None
    landing_url: str | None = None


class Claim(BaseModel):
    text: str
    type: str  # rating | price | availability | endorsement | statistic
    verified: bool | None = None
    actual_value: str | None = None
    source_url: str | None = None
    source_hash: str | None = None


class PipelineResult(BaseModel):
    ad_id: str
    verdict: Verdict
    scores: dict[str, float] = Field(default_factory=dict)  # contextual_safety, claim_truthfulness, ...
    claims: list[Claim] = Field(default_factory=list)
    reason: str = ""
    rule_fired: str = ""  # which deterministic rule produced the verdict
    vulnerability_flags: list[str] = Field(default_factory=list)


class Attestation(BaseModel):
    """Signed, replayable receipt for one verdict."""

    ad_id: str
    ad_hash: str  # sha256 of the ad creative
    verdict: Verdict
    result: PipelineResult
    models_used: dict[str, str] = Field(default_factory=dict)
    issued_at: str  # ISO 8601
    signature: str = ""  # ed25519 over the canonical payload
    public_key: str = ""
