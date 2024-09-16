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

"""
def init_db(conn):
    with conn.cursor() as curs:
        with open("../database.sql", "r") as f:
            sql = f.read()

        curs.execute(sql)
        conn.commit()
"""


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
    id = db.save(conn, url)

    flash("URL был успешно добавлен", "success")
    return redirect(url_for("show_url", id=id))


@app.route("/urls")
def show_urls():
    urls = db.get_all_urls(conn)
    return render_template("/urls/index.html", urls=urls)


@app.route("/urls/<int:id>")
def show_url(id):
    url = db.find(conn, id)

    if not url:
        flash("URL не найден", "error")
        return redirect(url_for("new_url"))

    return render_template("/urls/show.html", url=url)


def validate(url):
    errors = {}
    if "name" not in url or not url["name"]:
        errors["name"] = "URL не должен быть пустым"
    elif len(url["name"]) >= 255:
        errors["name"] = "URL должен быть короче 255 символов"
    return errors


if __name__ == "__main__":
    app.run(debug=True)
