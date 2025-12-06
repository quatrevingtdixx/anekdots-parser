import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


BASE_URL = "https://shytok.net/anekdots/anekdoty-pro-evreev"


def build_url(page):
    """Формирование URL: первая страница — без номера."""
    if page == 1:
        return f"{BASE_URL}.html"
    return f"{BASE_URL}-{page}.html"


def parse_page(url):
    """Парсинг одной страницы, возврат списка анекдотов."""
    jokes = []

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # ИЩЕМ ВСЕ БЛОКИ С АНЕКДОТАМИ
    blocks = soup.find_all("div", class_="text2")

    if not blocks:
        print(f"⚠ Анекдоты не найдены на {url}")
        return []

    for b in blocks:
        text = b.get_text("\n", strip=True)
        # фильтр чтобы убрать пустые элементы
        if text and len(text) > 3:
            jokes.append(text)

    print(f"Найдено анекдотов: {len(jokes)}")
    return jokes


def main():
    all_jokes = []

    for page in range(1, 90):
        url = build_url(page)
        print(f"\n=== Страница {page}/89: {url}")

        jokes = parse_page(url)
        all_jokes.extend(jokes)

        time.sleep(0.5)  # ограничение по скорости

    print(f"\nВсего собрано анекдотов: {len(all_jokes)}")

    df = pd.DataFrame(all_jokes)
    df.to_excel("anekdots_evreev.xlsx", index=False, header=False)

    print("\nФайл anekdots_evreev.xlsx сохранён!")


if __name__ == "__main__":
    main()
