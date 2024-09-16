import psycopg2
from psycopg2.extras import RealDictCursor


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
        return id


def find(conn, id):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            SELECT * FROM urls
            WHERE id = %s
            """,
            (id,),
        )
        result = curs.fetchone()
        return result


def find_matches(conn, name):
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT * FROM urls
            WHERE name = %s
            """,
            (name,),
        )
        return curs.fetchone() is not None


def get_all_urls(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            SELECT * FROM urls;
            """
        )
        urls = curs.fetchall()
        return urls
