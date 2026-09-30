# app/ai/image_analyzer.py

import json
import os
import tempfile
import time

from app.services.image_loader import (
    download_temp_image
)

import os

from PIL import Image
import ollama


def analyze_image_once(image_path):

    # Open image
    img = Image.open(image_path)

    # Resize before sending to MiniCPM-V
    img.thumbnail((512, 512), Image.Resampling.LANCZOS)

    # JPEG does not support transparency
    if img.mode in ("RGBA", "LA", "P"):
        
        if img.mode == "P":
            img = img.convert("RGBA")

        background = Image.new("RGB", img.size, "white")
        background.paste(
            img,
            mask=img.getchannel("A")
        )

        img = background

    else:
        img = img.convert("RGB")

    # Create temporary JPEG
    tmp = tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    )

    tmp_path = tmp.name
    tmp.close()

    # Save resized RGB image
    img.save(
        tmp_path,
        format="JPEG",
        quality=85,
        optimize=True
    )

    prompt = """
Analyze this product image.

Return ONLY valid JSON.
Do not include markdown, explanations, or additional text.

Use exactly this structure:

{
  "surface_analysis": {
    "main_surface": "",
    "secondary_surface": "",
    "keep_unchanged": []
  },

  "visual_features": {
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
  },

  "taxonomy_search_description": ""
}

Rules for visual analysis:
- Identify what the product actually is.
- Describe only what is visually supported by the image.
- Do not invent specifications.
- Do not describe marketing claims.
- Use generic retail terminology.
- Use category/product terminology useful for taxonomy matching.
- Keep uncertain fields empty rather than guessing.
- "confidence" must be a number from 0 to 1.

Rules for taxonomy_search_description:
- Describe what the product IS.
- Do not describe marketing claims.
- Use generic retail terminology.
- Use category words.
- Include useful product-type, form-factor, material, construction, and usage terms when visually supported.
- Maximum 50 words.
"""

    start = time.time()

    try:

        response = ollama.chat(
            model="minicpm-v",
            format="json",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [tmp_path]
                }
            ],
            options={
                "temperature": 0,
                "seed": 45,
                "num_predict": 300
            }
        )

        print(
            "MINICPM-V TIME:",
            round(time.time() - start, 2),
            "sec"
        )

        content = response["message"]["content"]

        print("\nRAW MINICPM RESPONSE:")
        print(content)

        try:

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(content)

        except Exception as e:

            print("\nMINICPM JSON ERROR:")
            print(e)
            print("PROMPT LENGTH:", len(prompt))

            return {
                "surface_analysis": {
                    "main_surface": "main body",
                    "secondary_surface": "",
                    "keep_unchanged": ["logo"]
                },

                "visual_features": {
                    "product_type": "",
                    "size_category": "",
                    "portability": "",
                    "has_handle": False,
                    "has_wheels": False,
                    "foldable": False,
                    "mounted": False,
                    "material": "",
                    "construction": "",
                    "usage": "",
                    "confidence": 0
                }
            }

    finally:

        # Delete temporary JPEG
        try:
            os.remove(tmp_path)
        except OSError:
            pass