
# 🍽️ Food Macro

A full-stack web app that estimates the nutritional content of a meal from a photo.
Upload a picture of your food and get back a macro breakdown (calories, protein,
carbs, sugar, fat, fiber), an ingredient list, and a dish classification — powered
by Groq's vision-enabled LLM (`qwen/qwen3.8-27b`).

Access is gated behind GitHub OAuth with a user allowlist, so it runs as a private,
invite-only app.

## Demo

https://github.com/user-attachments/assets/4aa8606a-d3dc-45c6-a348-b047baf3e3a9

## Architecture

```
Browser ──> Vue 3 SPA (nginx) ──> FastAPI backend ──> Groq Vision API
                                        │
                                        └──> GitHub OAuth (login + allowlist)
```

- **Frontend** — Vue 3 + Vite single-page app, served by nginx in production.
- **Backend** — FastAPI, mounted under `/api`, talking to Groq for inference.
- **Auth** — GitHub OAuth; the access token is stored in an httponly cookie and
  re-verified on each request against an `ALLOWED_USERS` allowlist.

## Tech Stack

| Layer     | Tech                                             |
| --------- | ------------------------------------------------ |
| Frontend  | Vue 3, Vue Router, Vite                          |
| Backend   | FastAPI, Uvicorn, Python 3.11                    |
| AI        | Groq — `qwen/qwen3.8-27b` (vision)               |
| Auth      | GitHub OAuth                                     |
| Deploy    | Docker, Kubernetes, Flux (GitOps), Sealed Secrets |
| Tooling   | Ruff (Python), Prettier + ESLint (frontend)      |

## Project Structure

```
.
├── main.py                 # FastAPI app + routes
├── services/
│   ├── vision_service.py   # Groq image analysis
│   └── auth_service.py     # GitHub OAuth + allowlist
├── frontend/               # Vue 3 SPA
│   └── src/views/          # Home (login) + Analyze (upload/results)
├── scripts/
│   └── check_vision.py     # dev tool: smoke-test the Groq vision pipeline
├── docker-compose.yml      # backend + frontend
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+
- A [Groq API key](https://console.groq.com/keys) (free)
- A [GitHub OAuth App](https://github.com/settings/developers) for local development,
  with the callback URL set to `http://localhost:8080/callback`. Use a separate app
  from production: an OAuth App only accepts its one registered callback URL.

### Configuration

Create a `.env` in the project root for the backend:

```env
GROQ_API_KEY=your_groq_api_key
GITHUB_CLIENT_ID=your_dev_oauth_client_id
GITHUB_CLIENT_SECRET=your_dev_oauth_client_secret
ALLOWED_USERS=your_github_username,another_username
OAUTH_REDIRECT_URI=http://localhost:8080/callback
FRONTEND_URL=http://localhost:5173/food-macro
CORS_ORIGINS=http://localhost:5173
```

The backend refuses to start if any of these are missing.

The frontend reads its API base URL from a Vite env file per mode:

| File                        | Used by         | Value                       |
| --------------------------- | --------------- | --------------------------- |
| `frontend/.env.development` | `npm run dev`   | `VITE_API_URL=http://localhost:8080` |
| `frontend/.env.production`  | `npm run build` | your production API URL     |

`VITE_API_URL` is baked into the bundle at build time.

### Run the backend

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Interactive API docs: http://localhost:8080/docs

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173/food-macro/ (the dev server is pinned to port 5173 to
match `FRONTEND_URL` and `CORS_ORIGINS`).

### Production build with Docker

```bash
docker compose up --build
```

Frontend on `:5173`, backend on `:8080`. The frontend image is a production build,
so it uses `frontend/.env.production`. Use the dev servers above for local login.

## Deployment

Production runs on Kubernetes and is deployed through GitOps: Flux syncs the
cluster from a separate config repo. Secrets are stored there as Sealed Secrets,
and the backend's non-secret config (URLs, CORS) is set as plain environment
variables in the deployment manifest.

## Security

- GitHub OAuth login with `state` validation and a minimal `read:user` scope
- Access limited to an allowlist of GitHub users
- Session cookie is `HttpOnly` and `SameSite=Strict`
- CORS restricted to the app's own origin
- No secrets in the repo: `.env` is gitignored, production uses Sealed Secrets
- HTTPS enforced with HSTS

## API Reference

All routes are served under the `/api` prefix.

| Method | Endpoint         | Auth | Description                               |
| ------ | ---------------- | ---- | ----------------------------------------- |
| POST   | `/analyze-image` | ✅   | Upload an image, get macro estimates back |
| GET    | `/login`         | —    | Redirect to GitHub OAuth                  |
| GET    | `/callback`      | —    | OAuth callback; sets the session cookie   |
| GET    | `/me`            | ✅   | Return the logged-in user's username      |
| POST   | `/logout`        | —    | Clear the session cookie                  |

### `POST /analyze-image` response

```json
{
  "filename": "lunch.jpg",
  "analysis": {
    "success": true,
    "error": null,
    "data": {
      "title": "Chicken and rice",
      "dish_type": "homemade",
      "confidence": 0.85,
      "summary": "...",
      "ingredients": ["chicken", "rice"],
      "estimated_macros": {
        "calories": 520, "protein_g": 40, "carbs_g": 55,
        "sugar_g": 6, "fat_g": 14, "fiber_g": 3
      }
    }
  }
}
```

## Development

Formatting and linting are enforced via a pre-commit hook:

```bash
pip install pre-commit && pre-commit install   # one-time setup
```

- **Python** — `ruff format .` and `ruff check --fix .`
- **Frontend** — `npm run format` (Prettier) and `npm run lint` (ESLint)

### Checking the vision pipeline

After changing the vision model or the prompt, sanity-check that image analysis
still works with a live Groq call (not an automated test — it costs tokens):

```bash
venv/bin/python scripts/check_vision.py                  # list available models
venv/bin/python scripts/check_vision.py path/to/food.jpg # run the real pipeline
```

## Roadmap

- [ ] Persist analyses to Postgres for meal history and daily macro totals
- [x] Make OAuth callback / CORS / redirect URLs environment-driven so login works
      in local development
