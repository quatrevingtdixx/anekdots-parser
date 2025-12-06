import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Список категорий для парсинга
CATEGORIES = {
    "evreev":         "https://shytok.net/anekdots/anekdoty-pro-evreev",
    "advokatov":      "https://shytok.net/anekdots/anekdoty-pro-advokatov",
    "armyan":         "https://shytok.net/anekdots/anekdoty-pro-armyan",
    "voennyih":       "https://shytok.net/anekdots/anekdoty-pro-voennyih",
    "zhivotnyh":      "https://shytok.net/anekdots/anekdoty-pro-zhivotnyh",
}

def build_url(base, page):
    """Страницы имеют формат category.html, category-2.html и т.д."""
    if page == 1:
        return f"{base}.html"
    return f"{base}-{page}.html"

def parse_page(url):
    """Парсит одну страницу и возвращает список анекдотов."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # Ищем текст всех анекдотов
    blocks = soup.find_all("div", class_="text2")
    jokes = []
    for b in blocks:
        text = b.get_text("\n", strip=True)
        if text and len(text) > 3:
            jokes.append(text)

    return jokes

def parse_category(name, base_url, max_pages=200):
    """Парсит все страницы одной категории."""
    all_jokes = []

    for page in range(1, max_pages + 1):
        url = build_url(base_url, page)
        print(f"\n[{name}] Страница {page}: {url}")

        jokes = parse_page(url)

        # Если страница пустая — значит пагинация закончилась
        if not jokes:
            print(f"[{name}] Конец страниц. Останов.")
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
            filename = os.path.join("output", f"anekdots_{name}.xlsx")
            df = pd.DataFrame(jokes, columns=["Анекдот"])
            df.to_excel(filename, index=False, header=False)
            print(f"[{name}] Сохранено {len(jokes)} анекдотов → {filename}")
        else:
            print(f"[{name}] Анекдоты не найдены!")

if __name__ == "__main__":
    main()
