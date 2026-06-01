# Sentinel Video Work Log

Purpose: track video-related files so agents do not confuse temporary capture/scaffold assets with the real product UI.

## Current Truth

- Layne's real pushed UI is in `frontend/`, added on `origin/main` by commits `502ad07` (`Add Next.js frontend with landing page and trace console demo.`) and `5419e9a` (`UI changes`).
- Do not treat the old static FastAPI `ui/` split-screen demo as the final product surface.
- `ui/` is Layne-owned per `AGENTS.md`. Any edits there need extra care and should be logged.
- The Remotion project in `sentinel-video/` is temporary video tooling, not Sentinel app source.

## Files Created Or Changed In This Pass

- `sentinel-video/`
  - Temporary Remotion project for video rendering experiments.
  - Status: provisional. Do not use for final render until it is rebuilt around Layne's actual UI.
- `sentinel-video/src/Composition.tsx`
  - Experimental composition. First version used abstract copy/cards; second version began pivoting to captured demo screenshots.
  - Status: reject for final; wrong source UI.
- `sentinel-video/src/index.css`
  - Experimental video styling.
  - Status: reject for final; tied to the wrong composition direction.
- `sentinel-video/package.json` and `package-lock.json`
  - Remotion dependencies installed after Ved explicitly approved npm package work.
  - Status: tooling only.
- `docs/assets/demo-*.png`
  - Screenshots captured from the current `/demo/` split-screen UI.
  - Status: documentation/demo placeholders only; not final video source unless Layne confirms this is the actual UI.
- `sentinel-video/public/assets/demo-*.png`
  - Copies of the same screenshots for Remotion.
  - Status: temporary render inputs.
- `ui/app.js`
  - Added `?scenario=<id>` support for deterministic screenshot capture.
  - Status: small utility edit, but it touches Layne-owned UI. Keep only if Layne/Ved want deterministic demo capture; otherwise remove.
- `frontend/`
  - Layne's actual Next.js frontend. Landing page at `/`; trace console at `/demo`.
  - Status: canonical UI source for the video unless Layne/Ved supersede it.
- `docs/assets/layne-ui/landing.png`
  - Screenshot captured from `http://127.0.0.1:3000/`.
  - Status: real Layne UI capture.
- `docs/assets/layne-ui/demo.png`
  - Screenshot captured from `http://127.0.0.1:3000/demo`.
  - Status: real Layne UI capture, pre-run trace state.
- `docs/assets/layne-ui/approve.png`, `vulnerability.png`, `false-claim.png`, `urgency.png`
  - Screenshots captured from Layne's `frontend/` trace console using `?capture=1`.
  - Status: real Layne UI capture, completed trace states.
- `docs/assets/demo-flow.mp4`
  - 28-second 1920x1080 Remotion video for the README, built from Layne UI captures.
  - Status: current README video asset.
- `docs/assets/demo-poster.png`
  - Poster frame extracted from `docs/assets/demo-flow.mp4`.
  - Status: current README poster image.

## Commands And Tooling Notes

- HyperFrames CLI was fetched via `npx --yes hyperframes doctor`; version reported `0.6.52`.
- Remotion project dependencies were installed with `npm i` under `sentinel-video/` after Ved explicitly waived the npm freeze for this video work.
- Remotion render was stopped after Ved clarified the UI source was wrong.
- The live FastAPI demo server was already running on port `8000` from PID `17527/17528` at the time of this log.
- `frontend` dependencies were installed with `npm install` after Ved explicitly approved package work for the video.
- `frontend` passed `npm run lint` and `npm run build`.
- The Next.js frontend dev server was run at `http://localhost:3000` for capture and then stopped.
- Added capture props to `frontend/src/app/demo/page.tsx`, `frontend/src/components/SentinelDashboard.tsx`, and `frontend/src/hooks/useSentinelDemo.ts` so README screenshots can render completed trace states deterministically with `?scenario=<id>&capture=1`.
- `sentinel-video` passed `npm run lint`.
- Render command: `npx remotion render SentinelLaunch ../docs/assets/demo-flow.mp4 --codec=h264 --crf=22 --concurrency=1`.
- Render output: `docs/assets/demo-flow.mp4`, 28.05s, 1920x1080, h264, about 10.9 MB.

## README GIF Pass (2026-05-28, prioritized over full video)

- Ved requested the README demo GIFs first (<5 min window); full motion-graphics launch video deferred.
- Recaptured Layne's real `/demo` at retina (3840×2160) via browser-harness + `?scenario=<id>&capture=1` into `docs/assets/layne-ui/v2/` (landing + 4 verdict states).
- Built 4 GIFs with ffmpeg `zoompan` (eased smoothstep camera moves) over the real captures, then Lanczos + diff-palette → GIF. No new deps; ffmpeg 8.0.1, no gifski.
  - `docs/assets/gifs/console-tour.gif` (1100px) — L→R pan + push-in across the full BLOCK console.
  - `docs/assets/gifs/pipeline.gif` (1000px) — push-in on the audit-trail span tree, settling on fixture-backed claim verification FAILED → `deterministic_gate` BLOCK.
  - `docs/assets/gifs/block-verdict.gif` (1000px) — zoom into BLOCKED verdict + signed `ed25519` receipt (`claim_truthfulness_failed`).
  - `docs/assets/gifs/approve-receipt.gif` (1000px) — zoom into APPROVE + signed receipt (`all_checks_passed`).
  - `.mp4` siblings kept alongside each GIF (smaller, for future `<video>` embeds).
- GIF sizes 4.6–5.7 MB each at 14fps; can be slimmed (12fps / narrower / fewer colors) if README weight matters.
- Embedded in a new README "## See it run" section, above "## What It Does", below the `demo-flow.mp4` placeholder.
- A clean HyperFrames project was scaffolded at `sentinel-video/sentinel-launch/` (blank, landscape) for the deferred motion-graphics video; not yet built out.

## Next Correct Step

Build the full ~60–75s motion-graphics launch video in `sentinel-video/sentinel-launch/` (HyperFrames, HTML-native) using the v2 retina captures + real scenario data; author its DESIGN.md from `frontend/src/app/globals.css` tokens. One open input: a music track (registry has none; do not pull copyrighted audio without Ved's source).
