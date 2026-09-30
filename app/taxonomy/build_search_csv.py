import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

query = """
SELECT
    b.id AS brick_id,

    s.segment_title,
    f.family_title,
    c.class_title,
    b.brick_title,

    b.includes_definition

FROM bricks b

JOIN classes c
    ON b.class_id = c.id

JOIN families f
    ON c.family_id = f.id

JOIN segments s
    ON f.segment_id = s.id
"""

df = pd.read_sql(query, conn)

conn.close()


df["search_text"] = (
    "Segment: " + df["segment_title"].fillna("") +
    "\nFamily: " + df["family_title"].fillna("") +
    "\nClass: " + df["class_title"].fillna("") +
    "\nBrick: " + df["brick_title"].fillna("") +
    "\nDefinition: " + df["includes_definition"].fillna("")
)

df = df[
    [
        "brick_id",
        "segment_title",
        "family_title",
        "class_title",
        "brick_title",
        "search_text"
    ]
]

output_file = "taxonomy_search.csv"

df.to_csv(
    output_file,
    index=False
)

print(f"Saved {len(df)} rows")
print("Saved to:", os.path.abspath(output_file))

print(
    f"Saved {len(df)} rows"
)