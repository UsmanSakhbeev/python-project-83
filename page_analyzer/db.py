def save(conn, url):
    if "id" not in url or not url["id"]:
        with conn.cursor() as curs:
            curs.execute(
                """
                INSERT INTO urls (name) VALUES (%s)
                RETURNING id
                """,
                (url["name"],),
            )
            id = curs.fetchone()[0]
            url["id"] = id
        conn.commit()
