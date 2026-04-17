# 🍽️ Food Macro Vision API

A REST API that analyzes food images and returns nutritional estimates using Groq's vision-enabled LLM (Llama 4 Scout). Upload a photo of any meal and get back macro breakdown, ingredient list, and dish classification.

## Features

- Identifies the dish and provides a short description
- Estimates macros: calories, protein, carbohydrates, sugar, fat, and fiber
- Classifies food origin: restaurant, home-cooked or unknown
- Returns a confidence score. Low-confidence results are rejected automatically

## Tech Stack

- **FastAPI** — REST API framework
- **Groq** — AI inference (Llama 4 Scout vision model)
- **Uvicorn** — ASGI server
- **Python 3.10+**

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ezbaa/food-macro-api.git
cd food-macro-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

You can get a free Groq API key at [console.groq.com](https://console.groq.com/keys).

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Reference

Once the server is running, open the interactive API docs in your browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

From there you can try out the `/analyze-image` endpoint directly by uploading an image file.

