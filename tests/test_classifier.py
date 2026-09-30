from taxonomy_matcher import find_matches

product = """
Professional Watercolor Brush Set
12 synthetic brushes for watercolor painting
"""

matches = find_matches(product)

for m in matches:

    print("\n----------------")

    print("Rank:", m["rank"])

    print("Distance:", m["distance"])

    print("Brick:", m["brick"])

    print(m["search_text"])