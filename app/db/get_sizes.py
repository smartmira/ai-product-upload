import psycopg2


def get_sizes(brick_name):

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sv.size_value

        FROM bricks b

        JOIN size_groups sg
        ON b.size_group_id = sg.id

        JOIN size_values sv
        ON sv.size_group_id = sg.id

        WHERE b.brick_title = %s

        ORDER BY sv.id
    """, (brick_name,))

    results = cursor.fetchall()

    conn.close()

    return [
        r[0]
        for r in results
    ]

print(
    get_sizes(
        "Mens Sneakers"
    )
)
print(
    get_sizes(
        "Kids Shoes"
    )
)
print(get_sizes("Dresses"))

print(get_sizes("Skirts"))

print(get_sizes("Trousers  & Shorts"))

print(
    get_sizes(
        "Shirts  & Blouses  & Polo Shirts  & T-shirts"
    )
)