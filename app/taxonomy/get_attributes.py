import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_attributes(brick_name):

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.attribute_title
        FROM attributes a
        JOIN bricks b
        ON a.brick_id = b.id
        WHERE b.brick_title = %s
    """, (brick_name,))

    rows = cursor.fetchall()

    conn.close()

    return [r[0] for r in rows]


print(
    get_attributes(
        "Artists Brushes & Applicators"
    )
)