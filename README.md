# 🍽️ Food Macro

A full-stack web app that estimates the nutritional content of a meal from a photo.
Upload a picture of your food and get back a macro breakdown (calories, protein,
carbs, sugar, fat, fiber), an ingredient list, and a dish classification — powered
by Groq's vision-enabled LLM (qwen/qwen3.6-27b).

Access is gated behind GitHub OAuth with a user allowlist, so it runs as a private,
invite-only app.

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
| AI        | Groq — `qwen/qwen3.6-27b` (vision)   |
| Auth      | GitHub OAuth                                      |
| Deploy    | Docker + Docker Compose (nginx for the frontend) |
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
- A [GitHub OAuth App](https://github.com/settings/developers) (Client ID + Secret)

### Configuration

Create a `.env` in the project root for the backend:

```env
GROQ_API_KEY=your_groq_api_key
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
ALLOWED_USERS=your_github_username,another_username
```

The frontend reads its API base URL from `frontend/.env`:

```env
VITE_API_URL=http://localhost:8080
```

> **Note:** the GitHub OAuth callback and CORS origin are currently hardcoded to the
> deployed domain, so the **login flow does not work locally yet**. Making these URLs
> environment-driven (so local login works) is tracked in the roadmap below.

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

App: http://localhost:5173/food-macro/

### Or run everything with Docker

```bash
docker compose up --build
```

Frontend on `:5173`, backend on `:8080`.

## API Reference

All routes are served under the `/api` prefix.

| Method | Endpoint         | Auth | Description                               |
| ------ | ---------------- | ---- | ----------------------------------------- |
| POST   | `/analyze-image` | ✅   | Upload an image, get macro estimates back |
| GET    | `/login`         | —    | Redirect to GitHub OAuth                  |
| GET    | `/callback`      | —    | OAuth callback; sets the session cookie   |
| GET    | `/me`            | ✅   | Return the logged-in user's username      |
| POST   | `/logout`        | ✅   | Clear the session cookie                  |

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
- [ ] Make OAuth callback / CORS / redirect URLs environment-driven so login works
      in local development (currently hardcoded to the production domain)
