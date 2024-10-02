import os

import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer import db

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def new_url():
    url = {"name": ""}
    errors = {}
    return render_template("/index.html", url=url, errors=errors)


@app.post("/")
def add_url():
    conn = db.connect_db(DATABASE_URL)
    url = request.form.to_dict()
    errors = validate(url)

    if errors:
        db.close(conn)
        return render_template("/index.html", url=url, errors=errors)
    existed_url = db.check_url_exists(conn, url["name"])

    if existed_url:
        flash("Страница уже существует", "info")
        id = existed_url["id"]
    else:
        id = db.insert_url(conn, url["name"])
        flash("URL был успешно добавлен", "success")

    db.close(conn)
    return redirect(url_for("show_url", id=id))


@app.route("/urls")
def show_urls():
    conn = db.connect_db(DATABASE_URL)
    urls = db.get_all_urls(conn)
    db.close(conn)
    return render_template("/urls/index.html", urls=urls)


@app.route("/urls/<int:id>")
def show_url(id):
    conn = db.connect_db(DATABASE_URL)
    url = db.find(conn, id)

    if not url:
        db.close(conn)
        flash("URL не найден", "error")
        return redirect(url_for("new_url"))

    db.close(conn)
    return render_template("/urls/show.html", url=url)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    conn = db.connect_db(DATABASE_URL)
    url_data = db.find(conn, id)
    url = url_data["name"]

    try:
        response = requests.get(url)
        response.raise_for_status()
        status_code = response.status_code

        soup = BeautifulSoup(response.text, "lxml")
        h1 = soup.h1.string if soup.h1 else None
        title = soup.title.string if soup.title else None
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else None

        db.insert_check(conn, id, status_code, h1, title, description)
        db.close(conn)
        flash("Проверка успешно пройдена", "succes")
    except requests.RequestException:
        db.close(conn)
        flash("Произошла ошибка при проверке", "error")
    return redirect(url_for("show_url", id=id))


def validate(url):
    errors = {}
    if "name" not in url or not url["name"]:
        errors["name"] = "URL не должен быть пустым"
    elif len(url["name"]) >= 255:
        errors["name"] = "URL должен быть короче 255 символов"
    return errors


if __name__ == "__main__":
    app.run(debug=True)
