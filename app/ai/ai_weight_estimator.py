from ollama import chat
import json
import re


def estimate_weight_ai(
    title,
    classification,
    dimensions
):

    prompt = f"""
Estimate realistic ecommerce shipping weight.

Title:
{title}

Classification:
{classification}

Dimensions:
{dimensions}

Return ONLY JSON.

Example:

{{
  "weight_kg": 0.85
}}
"""

    try:

        response = chat(
            model="gemma3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            options={
                "temperature": 0,
                "seed": 45,
            }
        )

        content = response["message"]["content"]

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if match:

            return json.loads(
                match.group()
            )

    except Exception as e:

        print(
            "Weight estimation error:",
            e
        )

    volume = (
        dimensions["length_cm"]
        * dimensions["width_cm"]
        * dimensions["height_cm"]
    )

    return {
        "weight_kg": round(
            volume / 5000,
            2
        )
    }