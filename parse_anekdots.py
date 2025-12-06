import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Заголовки — ОБЯЗАТЕЛЬНО!
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
}

CATEGORIES = {
    "evreev":    "https://shytok.net/anekdots/anekdoty-pro-evreev",
    "advokatov": "https://shytok.net/anekdots/anekdoty-pro-advokatov",
    "armyan":    "https://shytok.net/anekdots/anekdoty-pro-armyan",
    "voennyih":  "https://shytok.net/anekdots/anekdoty-pro-voennyih",
    "zhivotnyh": "https://shytok.net/anekdots/anekdoty-pro-zhivotnyh",
}

def build_url(base, page):
    if page == 1:
        return f"{base}.html"
    return f"{base}-{page}.html"


def parse_page(url):
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    blocks = soup.find_all("div", class_="text2")
    jokes = []

    for b in blocks:
        text = b.get_text("\n", strip=True)
        if text and len(text) > 3:
            jokes.append(text)

    return jokes


def parse_category(name, base_url, max_pages=200):
    all_jokes = []

    for page in range(1, max_pages + 1):
        url = build_url(base_url, page)
        print(f"\n[{name}] Страница {page}: {url}")

        jokes = parse_page(url)

        if not jokes:
            print(f"[{name}] Конец страниц.")
            break

        all_jokes.extend(jokes)
        time.sleep(0.5)

    return all_jokes


def main():
    os.makedirs("output", exist_ok=True)

    for name, base in CATEGORIES.items():
        print(f"\n=== Парсим категорию: {name} ===")

        jokes = parse_category(name, base)

        if jokes:
            filename = f"output/anekdots_{name}.xlsx"
            pd.DataFrame(jokes, columns=["Анекдот"]).to_excel(filename, index=False, header=False)
            print(f"[{name}] Сохранено {len(jokes)} анекдотов → {filename}")
        else:
            print(f"[{name}] Анекдоты НЕ найдены!")

if __name__ == "__main__":
    main()
