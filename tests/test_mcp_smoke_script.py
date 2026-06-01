from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.smoke_mcp_http import (
    redacted_mcp_url,
    require_verify_tool,
    validate_verify_result,
)
from sentinel.main import cors_origins_from_env


def test_redacted_mcp_url_removes_auth_query_and_fragment():
    redacted = redacted_mcp_url(
        "https://user:secret@example.com:8443/mcp?token=abc#fragment"
    )

    assert redacted == "https://example.com:8443/mcp"
    assert "secret" not in redacted
    assert "token" not in redacted


def test_require_verify_tool_has_actionable_error():
    with pytest.raises(SystemExit) as exc:
        require_verify_tool(["health"])

    assert "verify tool missing" in str(exc.value)
    assert "health" in str(exc.value)


def test_validate_verify_result_requires_signed_false_claim_block():
    result = SimpleNamespace(
        isError=False,
        structuredContent={
            "verdict": "BLOCK",
            "result": {"rule_fired": "false_claim"},
            "signature": "signed",
        },
    )

    content = validate_verify_result(result)

    assert content["verdict"] == "BLOCK"


def test_validate_verify_result_summarizes_failures_without_dumping_result():
    result = SimpleNamespace(
        isError=False,
        structuredContent={
            "verdict": "APPROVE",
            "result": {"rule_fired": "approve"},
            "signature": "signed",
            "sensitive": "do-not-print",
        },
    )

    with pytest.raises(SystemExit) as exc:
        validate_verify_result(result)

    message = str(exc.value)
    assert "expected signed BLOCK receipt" in message
    assert "APPROVE" in message
    assert "do-not-print" not in message


def test_cors_origins_from_env_defaults_to_demo_wildcard(monkeypatch):
    monkeypatch.delenv("SENTINEL_CORS_ORIGINS", raising=False)

    assert cors_origins_from_env() == ["*"]


def test_cors_origins_from_env_accepts_production_origins(monkeypatch):
    monkeypatch.setenv(
        "SENTINEL_CORS_ORIGINS",
        "https://publisher.example, https://ops.example",
    )

    assert cors_origins_from_env() == [
        "https://publisher.example",
        "https://ops.example",
    ]
