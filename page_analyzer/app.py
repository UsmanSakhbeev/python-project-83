import os

import requests
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for

from page_analyzer import db, utils

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def get_index():
    url = {"name": ""}
    errors = {}
    return render_template("/index.html", url=url, errors=errors)


@app.post("/")
def add_url():
    conn = db.connect_db(DATABASE_URL)
    url = request.form.to_dict()
    errors = utils.validate({"url": url["url"]})

    if errors:
        db.close(conn)
        return render_template("/index.html", url={"name": url["url"]}, errors=errors)
    existed_url = db.check_url_exists(conn, url["url"])

    if existed_url:
        flash("Страница уже существует", "info")
        id = existed_url["id"]
    else:
        id = db.insert_url(conn, url["url"])
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
        abort(404, description="URL не найден")

    db.close(conn)
    return render_template("/urls/show.html", url=url)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    conn = db.connect_db(DATABASE_URL)
    url_data = db.find(conn, id)
    url = url_data["name"]

    if not url_data:
        db.close(conn)
        abort(404, description="URL для проверки не найден")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        db.close(conn)
        flash("Произошла ошибка при проверке", "error")
        return redirect(url_for("show_url", id=id))

    status_code = response.status_code
    parsed_html = utils.parse_html(response)

    db.insert_check(
        conn,
        id,
        status_code,
        parsed_html["h1"],
        parsed_html["title"],
        parsed_html["description"],
    )
    db.close(conn)
    flash("Проверка успешно пройдена", "succes")
    return redirect(url_for("show_url", id=id))


if __name__ == "__main__":
    app.run(debug=True)
