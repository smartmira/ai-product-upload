import json

from ollama import chat


def classify_product(
    product_text,
    candidates
):

    candidate_list = "\n".join([
        f"""
    {i + 1}

    Distance: {round(c['distance'], 4)}

    Segment: {c['segment']}
    Family: {c['family']}
    Class: {c['class']}
    Brick: {c['brick']}

    Definition:
    {c['search_text']}
    """
        for i, c in enumerate(candidates)
    ])

    prompt = f"""
Product:

{product_text}

Candidate categories ranked by similarity.

{candidate_list}

Task:

1. Determine exactly what the product is.

2. For every candidate:

   - determine whether it matches the product
   - determine whether it contradicts the product

3. Reject any candidate that introduces attributes
not present in the product.

Examples:

Mattress ≠ Water Bed

Mattress ≠ Inflatable Bed

Mattress ≠ Baby Cot Mattress

Television ≠ Speaker

Shoes ≠ Socks

Fridge ≠ Microwave

4. Choose the most specific candidate that matches
the product description.

5. Distance should only be used when two candidates
describe the SAME product type.

Examples:

Mattress vs Mattress Topper
→ distance may be used

Laptop vs Smartphone
→ distance must NOT be used

Important:

Do not invent features.

If the product description says "mattress"
and does not mention:

- inflatable
- water-filled
- baby cot

then those candidates must be rejected.

Return ONLY valid JSON.

Example:

{{
  "segment": "Home & Office",
  "family": "Household & Office Furniture",
  "class": "Household Beds & Mattresses",
  "brick": "Household Mattresses"
}}

Do not return markdown.

Do not return explanations.

Do not return code fences.

Return JSON only.
"""

    print("\nCANDIDATE DEFINITIONS")

    for c in candidates:

        print("\n-------------------")
        print(c["brick"])
        print(c["search_text"])

    for c in candidates:
        print(
            c["brick"],
            c["distance"]
        )

    print("\nGEMMA PROMPT")
    print(prompt)
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

    content = response["message"]["content"].strip()

    print("\nRAW GEMMA RESPONSE:")
    print(content)

    try:

        if content.startswith("```"):

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        result = json.loads(content)

        print("\nGEMMA CHOSE:")
        print(result["brick"])

        return result

    except Exception as e:

        print("\nJSON PARSE FAILED")
        print(e)

        print("\nFALLING BACK TO TOP VECTOR MATCH")

        best = candidates[0]

        return {
            "segment": best["segment"],
            "family": best["family"],
            "class": best["class"],
            "brick": best["brick"]
        }