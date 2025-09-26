## HackerCodex — Frontend

SvelteKit app with a Mapbox map and a small UI around it.

### Requirements

- Node 18+ (or 20+)

### Setup

1. Install deps

```sh
npm install
```

2. Create `frontend/.env`:

```
PUBLIC_MAPBOX_TOKEN=YOUR_MAPBOX_PUBLIC_TOKEN_HERE
```

Get a token at `https://account.mapbox.com`.

### Scripts

- Dev: `npm run dev`
- Build: `npm run build`
- Preview: `npm run preview`
- Lint: `npm run lint`

Dev server proxies `/api` to `http://localhost:8000`.

### Notes

- Map lives in `frontend/src/components/Map.svelte` (client-only).
- Tailwind v4 via Vite plugin (no config file).
- Global styles in `frontend/src/app.css`.
