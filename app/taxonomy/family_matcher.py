import faiss
import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

family_df = pd.read_csv(
    BASE_DIR / "family_search.csv"
)

print(
    "ROWS:",
    len(family_df)
)

print(
    "UNIQUE FAMILIES:",
    family_df["family"].nunique()
)

embeddings = np.load(
    BASE_DIR / "family_embeddings.npy"
).astype("float32")

index = faiss.IndexFlatL2(
    embeddings.shape[1]
)

index.add(
    embeddings
)

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

def detect_candidate_families(
    product_text,
    k=20
):

    query_vector = model.encode(
        [product_text],
        convert_to_numpy=True
    ).astype("float32")

    distances, indices = index.search(
        query_vector,
        k
    )

    results = []

    for rank, idx in enumerate(indices[0]):

        distance = float(
            distances[0][rank]
        )

        family = family_df.iloc[idx]["family"]

        results.append({
            "family": family,
            "distance": distance
        })

    return results