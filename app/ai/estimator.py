from ollama import chat
import json
import hashlib
import os

CACHE_FILE = os.path.join(
    "app",
    "cache",
    "dimension_cache.json"
)


# ---------------------------------------------------------
# CACHE HELPERS
# ---------------------------------------------------------

def load_dimension_cache():

    if not os.path.exists(CACHE_FILE):
        return {}

    try:

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print("\nDIMENSION CACHE LOAD ERROR:")
        print(e)

        return {}


def save_dimension_cache(cache):

    os.makedirs(
        os.path.dirname(CACHE_FILE),
        exist_ok=True
    )

    temp_file = CACHE_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cache,
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        CACHE_FILE
    )


# ---------------------------------------------------------
# CREATE DETERMINISTIC PRODUCT KEY
# ---------------------------------------------------------

def make_dimension_key(
    title,
    description,
    classification
):

    data = {
        "title": (
            title or ""
        ).strip().lower(),

        "description": (
            description or ""
        ).strip().lower(),

        "classification": {
            "segment": classification.get(
                "segment",
                ""
            ),

            "family": classification.get(
                "family",
                ""
            ),

            "class": classification.get(
                "class",
                ""
            ),

            "brick": classification.get(
                "brick",
                ""
            )
        }
    }

    normalized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()

def estimate_dimensions(
    title,
    description,
    classification,
    visual_features,
    image_path=None,
    surface_analysis=None
):

    # --------------------------------
    # Classification
    # --------------------------------
    brick = classification.get(
        "brick",
        "Unknown"
    )

    # --------------------------------
    # Create cache key
    # --------------------------------
    cache_key = make_dimension_key(
        title,
        description,
        classification
    )

    cache = load_dimension_cache()

    # --------------------------------
    # CACHE HIT
    # --------------------------------
    if cache_key in cache:

        print("\n================================")
        print("DIMENSION CACHE HIT")
        print("================================")

        print("PRODUCT:", title)
        print("BRICK:", brick)

        print("\nRETURNING FROM CACHE:")
        print(json.dumps(cache[cache_key], indent=2))

        return cache[cache_key]

    # --------------------------------
    # CACHE MISS
    # --------------------------------
    print("\n================================")
    print("DIMENSION CACHE MISS")
    print("================================")

    print("PRODUCT:", title)
    print("BRICK:", brick)
    # --------------------------------
    # Debug
    # --------------------------------
    print("\nDIMENSION INPUTS")
    print("TITLE:", title)
    print("BRICK:", brick)

    print("\nCUSTOMER DESCRIPTION:")
    print(description)

    print("\nSURFACE:")
    print(surface_analysis)

    print("\nVISUAL FEATURES:")
    print(visual_features)

    # --------------------------------
    # Prompt
    # --------------------------------
    prompt = f"""
You are an ecommerce logistics estimator.

Estimate dimensions and weight using all available evidence.

TITLE:
{title}

CUSTOMER DESCRIPTION:
{description}

TAXONOMY BRICK:
{brick}


VISUAL FEATURES:
{json.dumps(visual_features, indent=2)}

SURFACE ANALYSIS:
{json.dumps(surface_analysis, indent=2)}

Reasoning:

Estimate realistic ecommerce dimensions and weight.

Return JSON only.

Rules:

- Use taxonomy heavily.
- Use visual features heavily.
- Use portability.
- Use material.
- Use construction.
- Use title.
- Use description.

Do NOT use brand-specific memorization.

Estimate from category and physical characteristics.

Examples:

Portable Speaker:
typically tabletop

Office Chair:
typically floorstanding

Running Shoe:
typically handheld

Microwave Oven:
typically tabletop

Coffee Table:
typically floorstanding

Shipping dimensions must exceed product dimensions.

Return JSON only.

{{
  "size_class":"",
  "product_weight_kg":0,

  "product_length_cm":0,
  "product_width_cm":0,
  "product_height_cm":0,

  "shipping_length_cm":0,
  "shipping_width_cm":0,
  "shipping_height_cm":0,

  "fragile":false,
  "confidence":0
}}
"""

    # --------------------------------
    # Call Gemma
    # --------------------------------
    response = chat(
        model="gemma3:4b",
        format={
            "type": "object",
            "properties": {
                "size_class": {"type": "string"},
                "product_weight_kg": {"type": "number"},
                "product_length_cm": {"type": "number"},
                "product_width_cm": {"type": "number"},
                "product_height_cm": {"type": "number"},
                "shipping_length_cm": {"type": "number"},
                "shipping_width_cm": {"type": "number"},
                "shipping_height_cm": {"type": "number"},
                "fragile": {"type": "boolean"},
                "confidence": {"type": "number"}
            },
            "required": [
                "size_class",
                "product_weight_kg",
                "product_length_cm",
                "product_width_cm",
                "product_height_cm",
                "shipping_length_cm",
                "shipping_width_cm",
                "shipping_height_cm",
                "fragile",
                "confidence"
            ]
        },
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0,
            "seed": 45,
            "top_k": 1,
            "top_p": 1,
            "num_predict": 120
        }
    )

    content = response["message"]["content"]

    print("\nDIMENSION RESPONSE:")
    print(content)

    # --------------------------------
    # Parse result
    # --------------------------------
    try:

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        content = content.strip()

        if content.count("{") > content.count("}"):
            content += "}"

        result = json.loads(content)

        print("\nFINAL DIMENSIONS FROM AI:")
        print(json.dumps(result, indent=2))

        print("\nFINAL DIMENSIONS:")
        print(result)

        required_fields = [
            "product_weight_kg",
            "product_length_cm",
            "product_width_cm",
            "product_height_cm",
            "shipping_length_cm",
            "shipping_width_cm",
            "shipping_height_cm"
        ]

        invalid_result = any(
            field not in result or result[field] <= 0
            for field in required_fields
        )

        if invalid_result:

            print("\nINVALID DIMENSION RESULT")
            print("AI returned zero or missing dimension values.")

            print("\nRESULT:")
            print(json.dumps(result, indent=2))

            return None


    except Exception as e:

        print("\nDIMENSION JSON ERROR:")
        print(e)

        print("\nFALLING BACK TO DEFAULTS")

        return {
            "size_class": "handheld",

            "product_weight_kg": 1.0,

            "product_length_cm": 20,
            "product_width_cm": 15,
            "product_height_cm": 10,

            "shipping_length_cm": 25,
            "shipping_width_cm": 20,
            "shipping_height_cm": 15,

            "fragile": False,

            "confidence": 0.3
        }

    cache[cache_key] = result

    print("\nSAVING TO CACHE:")
    print(json.dumps(result, indent=2))

    save_dimension_cache(cache)

    print("\n================================")
    print("DIMENSION RESULT CACHED")
    print("================================")


    return result