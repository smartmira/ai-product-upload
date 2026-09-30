import ollama


def generate_product_description(
    title,
    customer_description,
    classification,
    surface_analysis,
    image_path
):

    prompt = f"""
Product Title:
{title}

Customer Description:
{customer_description}

Classification:
{classification["brick"]}

Surface Analysis:
{surface_analysis}

Describe the product in detail.

Focus on:

- physical appearance
- size clues
- materials
- handles
- wheels
- portability
- speaker drivers
- storage capacity
- construction

Return only the description.
"""

    try:

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

        print("\nENHANCED DESCRIPTION:")
        print(content)

        return content

    except Exception as e:

        print(
            "DESCRIPTION ERROR:",
            e
        )

        return customer_description