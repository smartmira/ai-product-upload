import psycopg2


def get_colors():

    conn = psycopg2.connect(
        host="localhost",
        database="marketplace_taxonomy",
        user="postgres",
        password="SMirac_5555"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT color_name
        FROM colors
        ORDER BY id
    """)

    results = cursor.fetchall()

    conn.close()

    return [
        r[0]
        for r in results
    ]