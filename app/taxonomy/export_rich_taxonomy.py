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
    s.segment_title,
    f.family_title,
    c.class_title,

    b.id,
    b.brick_title,
    b.includes_definition,

    STRING_AGG(
        DISTINCT a.attribute_title,
        ' | ' ORDER BY a.attribute_title
    ) AS attributes,

    STRING_AGG(
        DISTINCT av.attribute_value_title,
        ' | ' ORDER BY av.attribute_value_title
    ) AS attribute_values

FROM bricks b

LEFT JOIN classes c
ON b.class_id = c.id

LEFT JOIN families f
ON c.family_id = f.id

LEFT JOIN segments s
ON f.segment_id = s.id

LEFT JOIN attributes a
ON a.brick_id = b.id

LEFT JOIN attribute_values av
ON av.attribute_id = a.id

GROUP BY
    s.segment_title,
    f.family_title,
    c.class_title,
    b.id,
    b.brick_title,
    b.includes_definition
"""

df = pd.read_sql(query, conn)

conn.close()

print(df.head())
print("\nRows:", len(df))

df["attributes"] = df["attributes"].fillna("")
df["attribute_values"] = df["attribute_values"].fillna("")
df["includes_definition"] = df["includes_definition"].fillna("")

df["search_text"] = (

    df["segment_title"] + " | " +

    df["family_title"] + " | " +

    df["class_title"] + " | " +

    df["brick_title"] + " | " +

    df["includes_definition"] + " | " +

    df["attributes"] + " | " +

    df["attribute_values"]

)

df.to_csv(
    "taxonomy_search.csv",
    index=False
)

print("Saved taxonomy_search.csv")
print("\nFIRST SEARCH TEXT:\n")
print(df.iloc[0]["search_text"])