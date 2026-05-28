# Sentinel Demo Runbook

## Local preflight

```bash
uv run --python 3.12 --with-requirements requirements.txt pytest -q
uv run --python 3.12 --with-requirements requirements.txt python -c "from sentinel.attest import write_private_key; write_private_key('keys/attest_ed25519')"
uv run --python 3.12 --with-requirements requirements.txt uvicorn sentinel.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/demo/
```

## Click path

1. `Laptop Clean`: APPROVE, signed receipt, two verified offline claims.
2. `Anxiety Block`: BLOCK from `vulnerability_auto_block`.
3. `False Rating`: BLOCK from `false_claim`, with `actual_value` set to `3.2 stars`.
4. `Urgency`: BLOCK from `urgency_manipulation`.
5. `Grey Zone`: ESCALATE from `grey_zone`; click `Block` or `Approve` to show human review recording.

## API checks

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/v1/audit/latest
curl -s http://127.0.0.1:8000/v1/thrad/mock?scenario_id=false_rating
```

## MCP local check

```bash
uv run --python 3.12 --with-requirements requirements.txt python - <<'PY'
from sentinel.mcp_server import verify

receipt = verify(
    ad_id="false_rating",
    conversation="User: recommend good noise-cancelling headphones.",
    ad_creative="SonicMax - #1 rated, 4.9 stars on Amazon!",
    advertiser="SonicMax",
)
print(receipt.verdict)
print(receipt.result.rule_fired)
print(bool(receipt.signature))
PY
```

Expected:

```text
Verdict.BLOCK
false_claim
True
```

## Hosted deploy handoff

Alpic needs the repo connected with these settings:

- `installCommand`: `uv venv && uv pip install -r requirements.txt`
- `startCommand`: `uv run python -m sentinel.mcp_server`
- `PORT`: `8000`
- `ENV`: `production`
- `ATTESTATION_PRIVATE_KEY_PEM`: paste the generated PEM contents as a secret

The remote smoke test is a MCP `verify(...)` call against `/mcp`.
