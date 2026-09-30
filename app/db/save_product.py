import psycopg2


def save_product(
    title,
    description,
    classification,
    selected_attributes
):
    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (
            title,
            description,
            segment,
            family,
            class,
            brick
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        title,
        description,
        classification["segment"],
        classification["family"],
        classification["class"],
        classification["brick"]
    ))

    product_id = cursor.fetchone()[0]

    for attribute_name, attribute_value in selected_attributes.items():

        cursor.execute("""
            INSERT INTO product_attributes (
                product_id,
                attribute_name,
                attribute_value
            )
            VALUES (%s,%s,%s)
        """, (
            product_id,
            attribute_name,
            attribute_value
        ))

    conn.commit()
    conn.close()

    return product_id