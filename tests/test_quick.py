import pandas as pd
import json

df = pd.read_csv(
    "taxonomy_family_keywords.csv"
)

family_keywords = {}

for family in df["family_title"].unique():

    family_rows = df[
        df["family_title"] == family
    ]

    keywords = []

    for brick in family_rows["brick_title"]:

        keywords.extend(
            brick.lower()
                 .replace("&", " ")
                 .replace("-", " ")
                 .split()
        )

    family_keywords[family] = sorted(
        list(set(keywords))
    )

with open(
    "taxonomy_family_keywords.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        family_keywords,
        f,
        indent=4,
        ensure_ascii=False
    )

print("JSON saved successfully")