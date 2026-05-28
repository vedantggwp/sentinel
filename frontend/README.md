# Sentinel Frontend

Split-screen hackathon demo: **conversation (left)** + **Overmind trace & receipt (right)**.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

- Landing: [http://localhost:3000](http://localhost:3000)
- Trace console (demo): [http://localhost:3000/demo](http://localhost:3000/demo)

## Demo flow

1. Pick a scenario from the dropdown (maps to `data/scenarios.json` in the repo root).
2. Click **Run evaluation** — trace steps animate, then the receipt appears.
3. **Approved** scenarios show a labeled **Sponsored** ad; **blocked** scenarios show a withheld ad + receipt.

## Structure

| Path | Purpose |
|------|---------|
| `src/components/` | UI panels (chat, ad slot, trace, receipt) |
| `src/data/scenarios.ts` | Demo fixtures until `POST /v1/analyze` is live |
| `src/lib/types.ts` | Types aligned with `sentinel/contracts.py` |
| `src/hooks/useSentinelDemo.ts` | Demo state + step animation |

## Backend integration (for Ved)

When `POST /v1/analyze` returns real data, replace the demo engine call in `useSentinelDemo` with:

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
