import json

with open(
    "app/taxonomy/taxonomy_family_keywords.json",
    "r"
) as f:
    FAMILY_KEYWORDS = json.load(f)


def detect_candidate_families(text):

    words = set(
        text.lower()
            .replace("-", " ")
            .split()
    )

    scores = {}

    for family, keywords in FAMILY_KEYWORDS.items():

        score = len(
            words.intersection(
                set(keywords)
            )
        )

        if score > 0:

            scores[family] = score

    return sorted(
        scores,
        key=scores.get,
        reverse=True
    )[:5]