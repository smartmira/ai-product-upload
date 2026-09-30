import json
import ollama


def extract_visual_features(image_path):

    prompt = """
Analyze this product image.

Return JSON only.

{
    "product_type": "",
    "size_category": "",
    "portability": "",
    "has_handle": false,
    "has_wheels": false,
    "foldable": false,
    "mounted": false,
    "material": "",
    "construction": "",
    "usage": "",
    "confidence": 0
}

Rules:

product_type:
Describe the product category.

Examples:
portable speaker
office chair
running shoe
microwave oven
coffee table

size_category must be one of:

- pocket
- handheld
- tabletop
- floorstanding
- industrial

portability must be one of:

- highly_portable
- portable
- semi_portable
- stationary

construction examples:

- rugged
- lightweight
- heavy_duty
- compact
- reinforced

usage examples:

- indoor
- outdoor
- commercial
- consumer

Do NOT estimate dimensions.
Do NOT estimate weight.

Return JSON only.
"""

    response = ollama.chat(
        model="qwen2.5vl",
        format="json",
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

    print("\nRAW VISUAL FEATURES:")
    print(content)

    try:

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(content)

        print("\nPARSED VISUAL FEATURES:")
        print(result)

        return result

    except Exception as e:

        print("\nVISUAL FEATURE ERROR:")
        print(e)

        return {
            "product_type": "",
            "size_category": "medium",
            "has_handle": False,
            "has_wheels": False,
            "portable": True,
            "material": "",
            "construction": "",
            "speaker_size": "",
            "confidence": 0.3
        }