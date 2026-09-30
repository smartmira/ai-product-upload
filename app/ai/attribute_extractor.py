from ollama import chat
import json

def extract_attributes(
    product_text,
    attribute_options
):

    prompt = f"""
Product:

{product_text}

Available attributes:

{json.dumps(attribute_options, indent=2)}

Choose the most appropriate value.

Return JSON only.
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