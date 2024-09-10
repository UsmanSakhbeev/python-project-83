import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer import db

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
conn = psycopg2.connect(DATABASE_URL)


def init_db(conn):
    with conn.cursor() as curs:
        with open("../database.sql", "r") as f:
            sql = f.read()

        curs.execute(sql)
        conn.commit()


def check_tables(conn):
    with conn.cursor() as curs:
        curs.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = curs.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])


@app.route("/")
def new_url():
    url = {"name": ""}
    errors = {}
    return render_template("/index.html", url=url, errors=errors)


@app.post("/")
def post_url():
    url = request.form.to_dict()
    errors = validate(url)

    if errors:
        return render_template("/index.html", url=url, errors=errors)
    db.save(conn, url)

    flash("URL был успешно добавлен", "success")
    return redirect(url_for("new_url"))


def validate(url):
    errors = {}
    if not len(url["name"]) < 255:
        errors["name"] = "URL must be shorter than 255 characters"
    return errors


if __name__ == "__main__":
    init_db(conn)  # Инициализация базы данных
    check_tables(conn)
    app.run(debug=True)
