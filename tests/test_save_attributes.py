from save_product import save_product

product_id = save_product(
    title="Professional watercolor brush set",

    description="Set of 12 artist watercolor brushes",

    classification={
        "segment":"Media & Creatives",
        "family":"Arts & Crafts  Supplies",
        "class":"Artists Painting & Drawing Supplies",
        "brick":"Artists Brushes & Applicators"
    },

    selected_attributes={
        "Type of Artists Brush & Applicator":
        "ARTISTS ROUND BRUSH"
    }
)

print(product_id)