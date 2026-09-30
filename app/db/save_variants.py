import psycopg2


def save_variants(
    product_id,
    sizes,
    colors,
    stock,
    price,
    image_url=""
):

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    for size in sizes:

        for color in colors:

            cursor.execute("""
                INSERT INTO product_variants (
                    product_id,
                    size,
                    color,
                    stock,
                    price,
                    image_url
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                product_id,
                size,
                color,
                stock,
                price,
                image_url
            ))

    conn.commit()
    conn.close()