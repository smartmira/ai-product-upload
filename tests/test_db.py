import json

with open(
    "app/taxonomy/taxonomy_family_keywords.json"
) as f:
    data = json.load(f)

print(data["Car Accessories and Maintenance"])