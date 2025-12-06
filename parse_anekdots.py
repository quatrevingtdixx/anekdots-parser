import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://shytok.net/anekdots/anekdoty-pro-evreev"

def page_url(page_num: int) -> str:
    if page_num == 1:
        return BASE_URL + ".html"
    return f"{BASE_URL}/page{page_num}.html"

def fetch_anekdots():
    anekdots = []

    for page in range(1, 90):
        url = page_url(page)
        print(f"Fetching page {page}: {url}")
        try:
            resp = requests.get(url)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')

            for div in soup.select("div.text"):
                text = div.get_text(strip=True)
                if text:
                    anekdots.append(text)

            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching page {page}: {e}")

    return anekdots

def save_to_excel(anekdots, filename="anekdots_evreev.xlsx"):
    df = pd.DataFrame({'Анекдот': anekdots})
    df.to_excel(filename, index=False, header=False)
    print(f"Saved {len(anekdots)} anekdots to {filename}")

if __name__ == "__main__":
    all_anekdots = fetch_anekdots()
    save_to_excel(all_anekdots)
