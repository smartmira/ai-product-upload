import json
import ollama


def analyze_product_image(image_path):

    prompt = """
Analyze this product image.

Identify:

1. Main colorable surface
2. Secondary colorable surface
3. Elements that should remain unchanged when creating color variants

Return ONLY valid JSON.

Example:

{
  "main_surface": "woven fabric body",
  "secondary_surface": "plastic side panels",
  "keep_unchanged": [
    "logo",
    "buttons",
    "ports"
  ]
}
"""

    response = ollama.chat(
        model="qwen2.5vl",
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }
        ],
        options={
                "temperature": 0,
                "seed": 45,
            }
    )

    content = response["message"]["content"]

    try:
        return json.loads(content)

    except Exception:

        return {
            "main_surface": "main product body",
            "secondary_surface": "secondary product parts",
            "keep_unchanged": [
                "logo",
                "branding"
            ]
        }