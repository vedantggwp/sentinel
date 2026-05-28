# Sentinel — DESIGN.md

## Register
Brand (landing) + Product (trace console at `/demo`).

## Scene
Compliance engineer or judge reviewing ad-safety traces on a laptop in a dim room. High contrast, low glare, information-dense. Not generic “devtools green.”

## Color strategy
**Committed** on dark: phosphor chartreuse for emphasis, teal for interactive chrome, coral for decline.

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#050506` | Page (neutral black) |
| `--highlight` | `#E8FF6B` | Headline markers, primary emphasis |
| `--accent` | `#5EEAD4` | Links, trace breadcrumbs, secondary CTAs |
| `--accent-hot` | `#FF6B4A` | Decline, urgency |
| `--approve` | `#5EEAD4` | Accept states |
| `--foreground` | `#F4F4F5` | Body text |
| `--muted` | `#A1A1AA` | Secondary |

## Typography
- Sans: Geist Sans (UI)
- Mono: Geist Mono (trace IDs, primitives)

## Bans (Impeccable)
No gradient text, no hero-metric template, no identical icon+title card grids without variation.
