# Sentinel Demo Runbook

## Local preflight

```bash
uv run --python 3.12 --with-requirements requirements.txt pytest -q
uv run --python 3.12 --with-requirements requirements.txt python -c "from sentinel.attest import write_private_key; write_private_key('keys/attest_ed25519')"
uv run --python 3.12 --with-requirements requirements.txt uvicorn sentinel.main:app --reload --port 8000
```

Set `CONTEXT_CLASSIFIER_BACKEND=auto` to use Thrad's pinned DistilBERT ONNX
model when the model cache/dependencies are available. Without that env value,
Sentinel stays on the deterministic keyword gate for offline-stable tests.

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

## Streamable HTTP MCP check

In a second terminal:

```bash
PORT=8765 uv run --python 3.12 --with-requirements requirements.txt python -m sentinel.mcp_server
```

Then run:

```bash
uv run --python 3.12 --with-requirements requirements.txt python scripts/smoke_mcp_http.py
```

Expected:

```text
tools=verify
verdict=BLOCK
rule_fired=false_claim
signed=true
```

For Alpic, set `MCP_URL` to the deployed `/mcp` URL and run the same script.

## Hosted deploy handoff

Use the README's Deploy on Alpic button, or import:

```text
https://github.com/vedantggwp/sentinel
```

Alpic needs the repo connected with these build settings:

- `installCommand`: `uv venv && uv pip install -r requirements.txt`
- `startCommand`: `uv run python -m sentinel.mcp_server`

Set these as Alpic dashboard environment variables:

- `PORT`: `8000`
- `ENV`: `production`
- `ATTESTATION_PRIVATE_KEY_PEM`: paste the generated PEM contents as a secret;
  if the dashboard only accepts one line, replace line breaks with literal `\n`

The remote smoke test is a MCP `verify(...)` call against `/mcp`.
