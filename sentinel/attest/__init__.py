from __future__ import annotations

import base64
import binascii
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from sentinel.config import settings
from sentinel.contracts import AdRequest, Attestation, PipelineResult
from sentinel.pipeline.context_gate import context_gate_model_metadata


def create_attestation(
    ad: AdRequest,
    result: PipelineResult,
    private_key_path: str | None = None,
) -> Attestation:
    attestation = Attestation(
        ad_id=ad.ad_id,
        ad_hash=_sha256(ad.ad_creative),
        verdict=result.verdict,
        result=result,
        models_used={
            "pipeline": "offline-deterministic-v0",
            **context_gate_model_metadata(result.scores),
        },
        issued_at=datetime.now(UTC).isoformat(),
    )

    private_key = _load_signing_key(private_key_path)
    if private_key is None:
        return (
            attestation  # no key configured -> unsigned receipt (local dev / no secret)
        )

    signature = private_key.sign(_canonical_payload(attestation))
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return attestation.model_copy(
        update={
            "signature": base64.b64encode(signature).decode("ascii"),
            "public_key": base64.b64encode(public_key).decode("ascii"),
        }
    )


def verify_attestation(attestation: Attestation) -> bool:
    if not attestation.signature or not attestation.public_key:
        return False

    try:
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(attestation.public_key)
        )
        signature = base64.b64decode(attestation.signature)
        unsigned = attestation.model_copy(update={"signature": "", "public_key": ""})
        public_key.verify(signature, _canonical_payload(unsigned))
    except (InvalidSignature, ValueError, binascii.Error):
        return False
    return True


def write_private_key(path: str) -> None:
    private_key = Ed25519PrivateKey.generate()
    payload = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key_path = Path(path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(payload)
    key_path.chmod(0o600)


def _canonical_payload(attestation: Attestation) -> bytes:
    data = attestation.model_dump(mode="json")
    data.pop("signature", None)
    data.pop("public_key", None)
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _load_signing_key(private_key_path: str | None) -> Ed25519PrivateKey | None:
    """Resolve the ed25519 signing key, or None if none is configured.

    Prefers a PEM file on disk; falls back to PEM material in
    ATTESTATION_PRIVATE_KEY_PEM (env) for hosted deploys (e.g. Alpic) where
    `keys/` is gitignored and never reaches the build.
    """
    path = private_key_path or settings.attestation_private_key_path
    if path and Path(path).exists():
        return _coerce_ed25519(
            serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
        )
    if settings.attestation_private_key_pem:
        pem = settings.attestation_private_key_pem.replace("\\n", "\n")
        return _coerce_ed25519(
            serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
        )
    return None


def _load_private_key(path: str) -> Ed25519PrivateKey:
    return _coerce_ed25519(
        serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
    )


def _coerce_ed25519(key: object) -> Ed25519PrivateKey:
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("attestation key must be ed25519")
    return key


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
