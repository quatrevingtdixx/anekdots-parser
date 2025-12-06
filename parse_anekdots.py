import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Работающие HTTP-заголовки — критично важно для GitHub Actions
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
}

# Полный список категорий
CATEGORIES = {
    "evreev": "https://shytok.net/anekdots/anekdoty-pro-evreev",
    "advokatov": "https://shytok.net/anekdots/anekdoty-pro-advokatov",
    "armyan": "https://shytok.net/anekdots/anekdoty-pro-armyan",
    "voennyih": "https://shytok.net/anekdots/anekdoty-pro-voennyih",
    "zhivotnyh": "https://shytok.net/anekdots/anekdoty-pro-zhivotnyh",

    "sherloka_holmsa": "https://shytok.net/anekdots/anekdoty-pro-sherloka-holmsa",
    "forex": "https://shytok.net/anekdots/anekdoty-pro-forex",
    "telefonnye_prikoly": "https://shytok.net/anekdots/telefonnye-prikoly",
    "religija": "https://shytok.net/anekdots/anekdoty-pro-religiju",
    "chukchu": "https://shytok.net/anekdots/anekdoty-pro-chukchu",
    "muzha_i_zhenu": "https://shytok.net/anekdots/anekdots-pro-mujaijenu",
    "blondinok": "https://shytok.net/anekdots/anekdoty-pro-blondinok",
    "zhenshchin": "https://shytok.net/anekdots/anekdoty-pro-zhenshchin",
    "lyubovnikov": "https://shytok.net/anekdots/anekdoty-pro-lyubovnikov",
    "policiju": "https://shytok.net/anekdots/anekdoty-pro-policiju",
    "kompjuternye": "https://shytok.net/anekdots/kompjuternye-anekdoty",
    "detej": "https://shytok.net/anekdots/anekdoty-pro-detej",
    "vinni_puha": "https://shytok.net/anekdots/anekdoty-pro-vinni-puha",
    "anglijskij_jumor": "https://shytok.net/anekdots/anglijskij-jumor",
    "chernyj_jumor": "https://shytok.net/anekdots/chernyj-jumor",
    "trjoh_bogatyrej": "https://shytok.net/anekdots/anekdoty-pro-trjoh-bogatyrej",
    "studentov": "https://shytok.net/anekdots/anekdoty-pro-studentov",
    "muzhchin": "https://shytok.net/anekdots/anekdoty-pro-muzhchin",
    "vrachej": "https://shytok.net/anekdots/anekdoty-pro-vrachej",
    "poshlye": "https://shytok.net/anekdots/poshlye-anekdoty",
    "vasilija_ivanovicha": "https://shytok.net/anekdots/anekdoty-pro-vasiliya-ivanovicha-i-petku",
    "narkomanov": "https://shytok.net/anekdots/anekdoty-pro-narkomanov",
    "molodozhenov": "https://shytok.net/anekdots/anekdoty-pro-molodozhenov",
    "ljubov_zla": "https://shytok.net/anekdots/anekdoty-ljubov-zla",
    "russkij_nemec_kitaec": "https://shytok.net/anekdots/vstretilis-russkij-nemec-kitaec",
    "teshchu": "https://shytok.net/anekdots/anekdoty-pro-teshchu",
    "shtirlica": "https://shytok.net/anekdots/anekdoty-pro-shtirlica",
    "vovochku": "https://shytok.net/anekdots/anekdoty-pro-vovochku",
    "poruchika_rzhevskogo": "https://shytok.net/anekdots/anekdoty-pro-poruchika-rzhevskogo",
    "pensionerov": "https://shytok.net/anekdots/anekdoty-pro-pensionerov",
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
        print(f"\n[{name}] Страница {page} → {url}")

        jokes = parse_page(url)
        if not jokes:
            print(f"[{name}] Пусто. Конец страниц.")
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
            print(f"[{name}] ✔ Сохранено {len(jokes)} анекдотов → {filename}")
        else:
            print(f"[{name}] ❌ Ничего не найдено!")

if __name__ == "__main__":
    main()
