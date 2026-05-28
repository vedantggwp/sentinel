# 🛡️ Sentinel

**An independent safety & claim-verification layer for ads served inside AI conversations.**

When an AI assistant serves a sponsored suggestion, who checks it's safe for the moment — and truthful? Sentinel sits between the ad network and the user: it reads the conversation context, fact-checks the ad's claims against the live web, and emits a **signed, auditable verdict** before the ad ever reaches the person.

Built for the Cursor × Thrad London Hackathon (May 2026).

[![Deploy on Alpic](https://assets.alpic.ai/button.svg)](https://app.alpic.ai/new/clone?repositoryUrl=https%3A%2F%2Fgithub.com%2Fvedantggwp%2Fsentinel)

## How it works

A request flows through a deterministic pipeline. The LLM stages produce **scores and evidence**; a deterministic gate makes the final APPROVE / BLOCK call — so every decision is reproducible and auditable.

```
ad (Thrad bid-request)
  → 1. Context Gate      fast vulnerability check (~20ms, no LLM): is this moment safe for ANY ad?
  → 2. Claim Extraction  pull verifiable claims from the ad creative
  → 3. Fact Verification check each claim against the live web (Tavily)
  → 4. Safety Judge      score contextual safety, claim truthfulness, urgency, tone-mimicry
  → Deterministic Gate   APPROVE / BLOCK from scores + hard rules (vulnerability = auto-block)
  → Signed Attestation   ed25519 receipt keyed to the ad: verdict, evidence, source hashes
  → Overmind trace       every decision traced, policy-scored, improved over time
```

The signed attestation is exposed as an **MCP tool** (`verify`), so any agent can call Sentinel before serving an ad.

## Quickstart

```bash
cp .env.example .env                 # fill in API keys (never commit .env)
uv pip install -r requirements.txt
uvicorn sentinel.main:app --reload --port 8000
open http://localhost:8000/demo/      # demo UI
pytest -q                            # tests
```

For a signed local receipt, generate a development ed25519 key before running
the API:

```bash
python -c "from sentinel.attest import write_private_key; write_private_key('keys/attest_ed25519')"
```

## Stack

FastAPI (Python 3.12) · **Tavily** (live claim verification) · **Overmind** (decision tracing + policy optimization) · **Alpic** (MCP deployment) · built in **Cursor**. Vanilla HTML/JS UI, no build step.

## Architecture principle

**The LLM may score; it never decides.** The final gate is deterministic code, and every verdict ships with a signed, replayable receipt. That's the line between a safety *slogan* and safety *infrastructure*.

## License

MIT — see [LICENSE](LICENSE).
