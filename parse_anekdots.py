import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://shytok.net/anekdots/anekdoty-pro-evreev"

def page_url(page_num: int) -> str:
    if page_num == 1:
        return BASE_URL + ".html"
    return f"{BASE_URL}/page{page_num}.html"

def fetch_page(url, retries=3):
    """Запрос страницы со стабильным поведением."""
    for attempt in range(1, retries + 1):
        try:
            print(f"  Attempt {attempt}: GET {url}")
            resp = requests.get(url, timeout=10)   # важный таймаут
            resp.encoding = "utf-8"
            return resp.text

        except Exception as e:
            print(f"    Error: {e}")
            time.sleep(2)

    print("  Failed to fetch page after retries.")
    return None

def fetch_anekdots():
    anekdots = []

    for page in range(1, 90):
        url = page_url(page)
        print(f"\nFetching page {page}/89: {url}")

        html = fetch_page(url)
        if html is None:
            print("  Skipping page.")
            continue

        soup = BeautifulSoup(html, 'html.parser')

        blocks = soup.select("div.text")
        print(f"  Found {len(blocks)} blocks")

        for div in blocks:
            text = div.get_text(strip=True)
            if text:
                anekdots.append(text)

        time.sleep(0.5)  # пауза, чтобы не заблокировали

    return anekdots

def save_to_excel(anekdots, filename="anekdots_evreev.xlsx"):
    df = pd.DataFrame({'Анекдот': anekdots})
    df.to_excel(filename, index=False, header=False)
    print(f"\nSaved {len(anekdots)} anekdots to {filename}")

if __name__ == "__main__":
    all_anekdots = fetch_anekdots()
    save_to_excel(all_anekdots)
