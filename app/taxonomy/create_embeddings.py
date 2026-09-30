import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

df = pd.read_csv(
    "app/taxonomy/taxonomy_search.csv"
)

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

embedding_texts = []

for _, row in df.iterrows():

    text = f"""
Product Type:
{row['brick_title']}

Category:
{row['class_title']}

Family:
{row['family_title']}

Description:
{row['search_text']}
"""

    embedding_texts.append(text)

embeddings = model.encode(
    embedding_texts,
    show_progress_bar=True,
    convert_to_numpy=True
)

np.save(
    "app/taxonomy/taxonomy_embeddings.npy",
    embeddings
)

print(
    f"Saved embeddings for {len(df)} bricks"
)