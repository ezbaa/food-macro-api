import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY missing")
    return Groq(api_key=api_key)


client = get_client()


def analyze_image(encoded_image: str):
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
            Analyze this food image and return a valid JSON object.

            TASK:
            Identify the dish and estimate nutritional information.

            FOOD CLASSIFICATION:
            - restaurant: clearly prepared/served food from restaurant
            - home: homemade or simple assembled food
            - unknown: unclear origin

            NUTRITION RULES:
            - Estimate realistic full portion values
            - Restaurant food = standard portion size
            - Home food = average portion, slightly conservative estimate
            - Desserts, sweets, fried foods → higher calorie and sugar/fat density
            - Estimate sugar as part of carbohydrates

            MACRO RULES:
            - calories: number (single value)
            - protein_g: number,
            - carbs_g: number,
            - sugar_g: number,
            - fat_g: number,
            - fiber_g: number

            INGREDIENT RULES:
            - Only include visible or highly likely ingredients
            - Do not guess complex hidden ingredients
            
            OUTPUT RULES:
            - Return ONLY valid JSON
            - No markdown, no explanations, no extra text
            - No ``` formatting

            CONFIDENCE:
            - 0.9–1.0 = very clear and obvious dish
            - 0.6–0.8 = likely but some uncertainty
            - <0.6 = unclear or mixed dish

            JSON FORMAT:
            {
            "title": "name of the dish",
            "dish_type": "restaurant | home | unknown",
            "confidence": 0.0-1.0,
            "summary": "short description of the meal",
            "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
            "estimated_macros": {
                "calories": number,
                "fat_g": number,
                "carbs_g": number,
                "sugar_g": number,
                "protein_g": number,
                "fiber_g": number
            }
            }
            """,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
        )
        raw_content = response.choices[0].message.content

        try:
            parsed = json.loads(raw_content)

            confidence = parsed.get("confidence", 0)

            if confidence < 0.5:
                return {
                    "success": False,
                    "data": None,
                    "error": "Could not identify food in image",
                }

            return {"success": True, "data": parsed, "error": None}

        except json.JSONDecodeError:
            return {
                "success": False,
                "data": None,
                "error": "Model did not return valid JSON",
                "raw_output": raw_content,
            }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Image analysis failed: {str(e)}",
        }
