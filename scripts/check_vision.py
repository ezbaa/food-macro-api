"""
check_vision.py — dev utility for the Groq image-analysis pipeline.

This is NOT an automated test: it makes a live Groq API call (costs tokens,
needs network, non-deterministic). Use it to sanity-check that image analysis
still works — handy after changing the vision model or editing the prompt in
services/vision_service.py.

Usage:
    python scripts/check_vision.py                      # list available models
    python scripts/check_vision.py path/to/food.jpg     # + run the real pipeline
    python scripts/check_vision.py food.jpg --raw MODEL  # + smoke-test one model
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# This file lives in <project>/scripts/, so the project root is one level up.
# Resolving it this way means the script works from any working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load the project's .env (for GROQ_API_KEY) BEFORE importing vision_service,
# because that module builds the Groq client at import time.
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from services.vision_service import analyze_image, client  # noqa: E402


def list_models():
    """Print every model the current GROQ_API_KEY can access."""
    print("=== Models available to your Groq key ===")
    for m in sorted(client.models.list().data, key=lambda x: x.id):
        print(f"  {m.id}")


def encode(image_path: Path) -> str:
    """Read an image and base64-encode it, the same way main.py does."""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def smoke_test_model(model_id: str, encoded: str):
    """Send the image to one model with a trivial prompt.

    Confirms the model is alive and accepts images, independent of the
    project's macro prompt and JSON parsing — useful when scouting a
    replacement model.
    """
    print(f"\n=== Smoke-testing model: {model_id} ===")
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What food is this? One sentence."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                        },
                    ],
                }
            ],
        )
        print("Image accepted:", resp.choices[0].message.content)
    except Exception as e:
        print(f"Failed: {e}")


def run_real_pipeline(encoded: str):
    """Run the project's actual analyze_image() — the real API code path."""
    print("\n=== Running analyze_image() from services/vision_service.py ===")
    result = analyze_image(encoded)
    if result.get("success"):
        print("Success. Parsed data:")
        print(json.dumps(result["data"], indent=2))
    else:
        print(f"{result.get('error')}")
        if result.get("raw_output"):
            print("--- raw model output ---")
            print(result["raw_output"])


def main():
    parser = argparse.ArgumentParser(
        description="Sanity-check the Groq vision pipeline."
    )
    parser.add_argument("image", nargs="?", help="Path to a food image (jpg/png).")
    parser.add_argument(
        "--raw",
        metavar="MODEL",
        help="Smoke-test this model id directly, bypassing analyze_image().",
    )
    args = parser.parse_args()

    list_models()

    if not args.image:
        print("\n(no image given — pass a path to analyze one)")
        return

    image_path = Path(args.image)
    if not image_path.exists():
        sys.exit(f"Image not found: {image_path}")

    encoded = encode(image_path)
    if args.raw:
        smoke_test_model(args.raw, encoded)
    run_real_pipeline(encoded)


if __name__ == "__main__":
    main()
