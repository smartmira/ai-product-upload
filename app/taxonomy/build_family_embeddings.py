import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_csv(
    BASE_DIR / "taxonomy_search.csv"
)

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

family_records = []

for family in df["family_title"].unique():

    family_rows = df[
        df["family_title"] == family
    ]

    family_text = f"""
    Family:
    {family}

    Classes:
    {' '.join(
        family_rows['class_title']
        .astype(str)
    )}

    Bricks:
    {' '.join(
        family_rows['brick_title']
        .astype(str)
    )}

    Search:
    {' '.join(
        family_rows['search_text']
        .astype(str)
    )}
    """

    family_records.append({
        "family": family,
        "family_text": family_text
    })

family_df = pd.DataFrame(
    family_records
)

embeddings = model.encode(
    family_df["family_text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)

family_df.to_csv(
    BASE_DIR / "family_search.csv",
    index=False
)

np.save(
    BASE_DIR / "family_embeddings.npy",
    embeddings
)

print(
    f"Built {len(family_df)} family embeddings"
)
for _, row in df.iterrows():

    if row["brick_title"] in [
        "Household Mattresses",
        "Bed Sheets & Valances"
    ]:

        print("\nBRICK:")
        print(row["brick_title"])

        print("\nSEARCH TEXT:")
        print(row["search_text"])

        print("\nEMBEDDING TEXT:")
        print(
            f"""
Family: {row['family_title']}
Class: {row['class_title']}
Brick: {row['brick_title']}
Search Text: {row['search_text']}
"""
        )
