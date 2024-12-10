import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db(DATABASE_URL):
    return psycopg2.connect(DATABASE_URL)


def close(conn):
    conn.close()


def insert_url(conn, url):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            INSERT INTO urls (name) VALUES (%s)
            RETURNING id
            """,
            (url,),
        )
        id = curs.fetchone()["id"]
        conn.commit()
        return id


def find(conn, url_id):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            SELECT * FROM urls
            WHERE id = %s
            """,
            (url_id,),
        )
        url = curs.fetchone()

        if not url:
            return None

        curs.execute(
            """
            SELECT * FROM url_checks
            WHERE url_id = %s
            """,
            (url_id,),
        )
        url["checks"] = curs.fetchall()
        return url


def check_url_exists(conn, name):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            SELECT * FROM urls
            WHERE name = %s
            """,
            (name,),
        )
        return curs.fetchone()


def get_all_urls(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            SELECT
                urls.id,
                urls.name,
                last_checks.created_at,
                last_checks.status_code
            FROM urls
            LEFT JOIN (
                SELECT DISTINCT ON (url_id)
                    url_id,
                    created_at,
                    status_code
                FROM url_checks
                ORDER BY url_id, created_at DESC
            ) AS last_checks
            ON urls.id = last_checks.url_id
            ORDER BY urls.id;
            """
        )
        urls = curs.fetchall()
        return urls


def insert_check(conn, url_id, status_code, h1=None, title=None,
                 description=None):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            """
            INSERT INTO
            url_checks (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (url_id, status_code, h1, title, description),
        )
        conn.commit()
