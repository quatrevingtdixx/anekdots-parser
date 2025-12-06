import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://shytok.net/anekdots/anekdoty-pro-evreev"

def page_url(page_num: int) -> str:
    if page_num == 1:
        return BASE_URL + ".html"
    return f"{BASE_URL}-{page_num}.html"

def clean_html_block(html_block):
    """Чистит HTML и разбивает анекдоты по <br><br>."""
    # Преобразуем в soup
    soup = BeautifulSoup(html_block, "html.parser")

    # Удаляем мусорные блоки
    for tag in soup.find_all(["h1", "center", "script", "span", "div"]):
        tag.decompose()

    # Получаем HTML без них
    cleaned_html = str(soup)

    # Разделяем анекдоты
    raw_parts = cleaned_html.split("<br><br>")

    # Преобразуем каждую часть в текст
    final_texts = []
    for part in raw_parts:
        text = BeautifulSoup(part, "html.parser").get_text(strip=True)
        if text and len(text) > 3:
            final_texts.append(text)

    return final_texts


def fetch_anekdots():
    all_anekdots = []

    for page in range(1, 90):
        url = page_url(page)
        print(f"\n=== Fetching page {page}/89: {url}")

        try:
            resp = requests.get(url, timeout=10)
        except Exception as e:
            print(f"  ERROR: failed to request page: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        content = soup.find("div", id="dle-content")
        if not content:
            print("  ERROR: <div id='dle-content'> not found")
            continue

        anekdots = clean_html_block(str(content))
        print(f"  Found {len(anekdots)} jokes on this page")

        all_anekdots.extend(anekdots)

        time.sleep(0.5)

    return all_anekdots


def save_to_excel(anekdots, filename="anekdots_evreev.xlsx"):
    df = pd.DataFrame({"Анекдот": anekdots})
    df.to_excel(filename, index=False, header=False)
    print(f"\n=== Saved {len(anekdots)} анекдотов в {filename}")


if __name__ == "__main__":
    jokes = fetch_anekdots()
    save_to_excel(jokes)
