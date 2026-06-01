# Sentinel Frontend

Split-screen hackathon demo: **conversation (left)** + **audit trace & receipt (right)**.

## Run locally

**Terminal 1 — API (required for live mode)**

```bash
cd ..  # repo root
uv run --python 3.12 --with-requirements requirements.txt uvicorn sentinel.main:app --reload --port 8000
```

**Terminal 2 — Next.js UI**

```bash
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

- Landing: [http://localhost:3000](http://localhost:3000)
- Trace console: [http://localhost:3000/demo](http://localhost:3000/demo)

The demo shows an **api** badge when connected to the backend; **offline** uses local fixtures only.

**Ved’s vanilla UI (reference implementation)**

```text
http://127.0.0.1:8000/demo/
```

## Demo flow

1. Pick a scenario from the dropdown (maps to `data/scenarios.json` in the repo root).
2. Click **Run evaluation** — trace steps animate, then the receipt appears.
3. **Approved** scenarios show a labeled **Sponsored** ad; **blocked** scenarios show a withheld ad + receipt.

## Structure

| Path | Purpose |
|------|---------|
| `src/components/` | UI panels (chat, ad slot, trace, receipt) |
| `src/data/scenarios.ts` | Demo fixtures with API mapping when `POST /v1/analyze` is reachable |
| `src/lib/types.ts` | Types aligned with `sentinel/contracts.py` |
| `src/hooks/useSentinelDemo.ts` | Demo state + step animation |

## Backend integration (for Ved)

When `POST /v1/analyze` is reachable, `useSentinelDemo` maps the API response into the same trace UI shape:

```ts
fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/analyze`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    ad_id: scenario.id,
    conversation: scenario.messages.map((m) => `${m.role}: ${m.content}`).join("\n"),
    ad_creative: `${scenario.candidateAd.headline} — ${scenario.candidateAd.body}`,
    advertiser: scenario.candidateAd.advertiser,
  }),
});
```

Map the API `PipelineResult` + attestation into `EvaluationResult` (see `src/lib/types.ts`).

## Deploy

```bash
npm run build
# Vercel: set root directory to `frontend`
```
