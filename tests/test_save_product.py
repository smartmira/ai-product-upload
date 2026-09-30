# test_save_product.py

from save_product import save_product

product = {
    "title": "Professional watercolor brush set",
    "description": "Set of 12 artist watercolor brushes"
}

classification = {
    "segment": "Media & Creatives",
    "family": "Arts & Crafts  Supplies",
    "class": "Artists Painting & Drawing Supplies",
    "brick": "Artists Brushes & Applicators"
}

save_product(
    title=product["title"],
    description=product["description"],
    classification=classification,
    selected_attributes={}
)