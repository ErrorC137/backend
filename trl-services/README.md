# MatDAO TRL Services

Standalone API for TRL evaluation storage, milestone verification (AI Auditor), co-founder matching, and the R2C Commercialization Leaderboard.

## Local development

```bash
npm install
cp .env.example .env
npm run dev
```

Default port: **3001** (`TRL_SERVICES_PORT`). On Render, `PORT` is set automatically.

## Deploy on Render

1. Create a **Web Service** from this directory (or use root `render.yaml`).
2. Build: `npm install && npm run build`
3. Start: `npm start`
4. Set env vars:
   - `GEMINI_API_KEY` (optional — heuristic fallback works)
   - `ALLOWED_ORIGINS` = your v0/Vercel frontend URL

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health |
| POST | `/api/evaluate` | TRL evaluation + milestone mapping |
| GET | `/api/projects` | R2C leaderboard projects |
| GET/POST | `/api/verify` | AI Auditor |
| POST | `/api/verify/:id/vote` | Human reviewer vote |
| GET | `/api/researchers` | Co-founder profiles |
| POST | `/api/match` | Co-founder matching |

## Frontend proxy

The Next.js frontend proxies via `/api/trl-services/*`. Set `TRL_SERVICES_URL` to your Render URL in Vercel/v0.
