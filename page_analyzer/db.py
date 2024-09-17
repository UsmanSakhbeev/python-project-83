import psycopg2
from psycopg2.extras import RealDictCursor


def insert_url(conn, url):
    with conn.cursor() as curs:
        curs.execute(
            """
            INSERT INTO urls (name) VALUES (%s)
            RETURNING id
            """,
            (url,),
        )
        id = curs.fetchone().id
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


def check_url_exists(conn, name):
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
