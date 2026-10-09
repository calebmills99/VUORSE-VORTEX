# Sixth Intergalactic Summit Chamber

Staging the **Sixth Galactic Summit** (called p.37, never fully held — open thread).
Steward premise: delayed by an **intergalactic traffic jam**; chamber opens anyway.

- Session card: `src/summit/session.ts`
- Forge docket: `worldforge/2026-09-08-sixth-summit/` (lore simulation — not auto-canon)

Host attendees in the browser and **summon** their real processes via a local launcher.

Visual language ports the published Make kiosk:
https://kiosk-invert-94371455.figma.site

## Two processes

```bash
cd web
npm run summit:launcher   # terminal 1 — http://127.0.0.1:8788
npm run dev               # terminal 2 — http://127.0.0.1:5173
```

Vite proxies `/api/summit/*` → the launcher. The UI polls `/api/summit/health`; when it says **online**, **Summon process** works.

## UX

- Scroll-snap kiosk: Hero (Summit 6 + jam board) → Council → Golden Path → Declaration
- Click a seat → modal (franchise / invoke / **Summon process**)
- Floating **Chamber floor** chat (bottom-right)
- VUORSE + FCVW answer via Ollama; other seats stub + Summon

## What Summon does

| Seat | Action |
|------|--------|
| Voxtral / Grok / Claude / Codex / Ollama seats | New Windows Terminal (`wt`) with the CLI |
| OpenClaw / GPT | Opens URL in browser |
| Gray Eye | Opens Cursor on the repo (then run `/gandalf-the-gray-eye`) |
| Steward | No-op (you're it) |
| Otter | Opens the installed Ottermind desktop |

Allowlist lives in `summit-launcher.mjs` — no free-form shell from the browser.

## Figma

- Design file frame: https://www.figma.com/design/mvchcZFEp8Y4XC0v0L4oPl?node-id=1-2
- Make publish (kiosk invert): https://kiosk-invert-94371455.figma.site

## Files

- `src/summit/session.ts` — Sixth Summit session card
- `src/summit/attendees.ts` — roster + franchise + taglines
- `src/summit/ChamberChat.tsx` — floating floor UI
- `summit-launcher.mjs` — process bridge + chat + Ollama replies
- `src/App.tsx` — kiosk shell + seat modal + Summon
