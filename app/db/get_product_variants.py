import psycopg2


def get_product_variants(product_id):

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            size,
            color,
            stock,
            price,
            image_url
        FROM product_variants
        WHERE product_id = %s
    """, (product_id,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "size": r[0],
            "color": r[1],
            "stock": r[2],
            "price": float(r[3]),
            "image_url": r[4]
        }
        for r in rows
    ]