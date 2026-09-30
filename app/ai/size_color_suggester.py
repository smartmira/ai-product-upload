from ollama import chat
import json


def suggest_sizes_and_colors(
    product_text,
    sizes,
    colors
):

    prompt = f"""
Product:

{product_text}

Available sizes:

{json.dumps(sizes, indent=2)}

Available colors:

{json.dumps(colors, indent=2)}

Choose the most likely sizes and colors.

Return JSON only:

{{
  "suggested_sizes": [],
  "suggested_colors": []
}}
"""

    response = chat(
        model="gemma3:1b",
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

    return json.loads(
        response["message"]["content"]
    )