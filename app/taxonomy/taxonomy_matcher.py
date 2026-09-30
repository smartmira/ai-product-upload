import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from pathlib import Path

from app.taxonomy.family_matcher import (
    detect_candidate_families
)


BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# LOAD TAXONOMY DATA
# ============================================================

df = pd.read_csv(
    BASE_DIR / "taxonomy_search.csv"
)

embeddings = np.load(
    BASE_DIR / "taxonomy_embeddings.npy"
).astype("float32")


# Make sure embeddings and dataframe have the same number of rows
if len(df) != len(embeddings):
    raise ValueError(
        f"Taxonomy mismatch: "
        f"{len(df)} dataframe rows but "
        f"{len(embeddings)} embeddings."
    )


# ============================================================
# GLOBAL FAISS INDEX
# ============================================================

index = faiss.IndexFlatL2(
    embeddings.shape[1]
)

index.add(embeddings)


# ============================================================
# EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)


# ============================================================
# FIND TAXONOMY MATCHES
# ============================================================

def find_matches(
    product_text,
    k=20
):

    # --------------------------------------------------------
    # 1. Detect candidate families
    # --------------------------------------------------------

    filtered_df = df.copy()


    # --------------------------------------------------------
    # 4. Preserve ORIGINAL dataframe indices
    # --------------------------------------------------------

    original_indices = filtered_df.index.to_numpy()

    filtered_embeddings = embeddings[
        original_indices
    ]


    # --------------------------------------------------------
    # 5. Build temporary FAISS index
    # --------------------------------------------------------

    temp_index = faiss.IndexFlatL2(
        filtered_embeddings.shape[1]
    )

    temp_index.add(
        filtered_embeddings
    )


    # --------------------------------------------------------
    # 6. Encode product query
    # --------------------------------------------------------

    print("\nEMBEDDING QUERY")
    print(product_text)

    query_vector = model.encode(
        [product_text],
        convert_to_numpy=True
    ).astype("float32")


    # --------------------------------------------------------
    # 7. Limit k to available results
    # --------------------------------------------------------

    search_k = min(
        k,
        len(filtered_df)
    )


    distances, indices = temp_index.search(
        query_vector,
        search_k
    )

    # --------------------------------------------------------
    # 8. Build results
    # --------------------------------------------------------

    results = []

    for rank, idx in enumerate(indices[0]):

        if idx < 0:
            continue


        # IMPORTANT:
        # idx refers to filtered_embeddings,
        # so retrieve from filtered_df.
        row = filtered_df.iloc[idx]


        results.append({
            "rank": rank + 1,

            "distance": float(
                distances[0][rank]
            ),

            "segment": row["segment_title"],

            "family": row["family_title"],

            "class": row["class_title"],

            "brick": row["brick_title"],

            "search_text": row["search_text"]
        })


    return results