import psycopg2
import os
from dotenv import load_dotenv
import json

load_dotenv()


def get_attribute_values(brick_name):

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.id,
            a.attribute_title,
            av.attribute_value_title

        FROM attributes a

        JOIN attribute_values av
        ON av.attribute_id = a.id

        JOIN bricks b
        ON a.brick_id = b.id

        WHERE b.brick_title = %s

        ORDER BY
            a.id,
            av.attribute_value_title
    """, (brick_name,))

    rows = cursor.fetchall()

    conn.close()

    result = {}

    result = {}

    for attribute_id, attribute, value in rows:

        if attribute_id not in result:

            result[attribute_id] = {
                "name": attribute,
                "values": set()
            }

        result[attribute_id]["values"].add(value)

    clean_result = {}

    for attr in result.values():

        clean_result[attr["name"]] = sorted(
            list(attr["values"])
        )

    print("\nATTRIBUTE VALUES:")
    print(json.dumps(clean_result, indent=2))

    return clean_result

print(
    get_attribute_values(
        "Portable Speakers"
    )
)


