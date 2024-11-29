from bs4 import BeautifulSoup


def parse_html(html_content):
    soup = BeautifulSoup(html_content.text, "lxml")
    h1 = soup.h1.string if soup.h1 else None
    title = soup.title.string if soup.title else None
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"] if description_tag else None
    return {"h1": h1, "title": title, "description": description}


def validate(url):
    errors = {}
    if "url" not in url or not url["url"]:
        errors["url"] = "URL не должен быть пустым"
    elif len(url["url"]) >= 255:
        errors["url"] = "URL должен быть короче 255 символов"
    return errors
