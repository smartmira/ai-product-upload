import psycopg2


def get_product_images(product_id):

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT image_url
        FROM product_variants
        WHERE product_id = %s
        ORDER BY image_url
    """, (product_id,))

    results = cursor.fetchall()

    conn.close()

    return [
        r[0]
        for r in results
        if r[0]
    ]