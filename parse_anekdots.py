import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import sys
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
}

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

OUTDIR = "output"
os.makedirs(OUTDIR, exist_ok=True)

MAX_PAGES = 200
REQUEST_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds


def build_url(base, page):
    if page == 1:
        return f"{base}.html"
    return f"{base}-{page}.html"


def fetch_with_retries(url, retries=REQUEST_RETRIES):
    backoff = INITIAL_BACKOFF
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=12, headers=HEADERS)
            # Если 404 — страница реально не существует, считаем это "пустой" (конец пагинации)
            if resp.status_code == 404:
                return [], 404
            resp.raise_for_status()
            return resp.text, resp.status_code
        except requests.exceptions.HTTPError as he:
            status = None
            if he.response is not None:
                status = he.response.status_code
            # если 404, вернуть как empty (конец)
            if status == 404:
                return [], 404
            # для остальных HTTP ошибок пробуем ретрай
            print(f"[WARN] HTTPError {status} for {url} (attempt {attempt}/{retries})")
        except requests.exceptions.RequestException as re:
            print(f"[WARN] RequestException for {url}: {re} (attempt {attempt}/{retries})")
        # backoff before retry (except last attempt)
        if attempt < retries:
            time.sleep(backoff)
            backoff *= 2
    # все попытки не удались
    return None, None


def parse_page(url):
    html_or_list, status = fetch_with_retries(url, retries=REQUEST_RETRIES)
    # статус 404 -> интерпретируем как пустую страницу (конец пагинации)
    if status == 404:
        # Возвращаем пустой список, caller остановит пагинацию
        return []
    if html_or_list is None:
        # реальная сетевая/прочая ошибка после всех ретраев — возвращаем None чтобы caller продолжил аккуратно
        return None

    html = html_or_list
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.find_all("div", class_="text2")
    jokes = []
    for b in blocks:
        text = b.get_text("\n", strip=True)
        if text and len(text) > 3:
            jokes.append(text)
    return jokes


def parse_category(name, base_url, max_pages=MAX_PAGES):
    print(f"[{name}] start parsing")
    all_jokes = []
    seen = set()

    for page in range(1, max_pages + 1):
        url = build_url(base_url, page)
        print(f"[{name}] page {page} -> {url}")

        res = parse_page(url)
        # None = сетевой/неисправимая ошибка (после ретраев) — пропустить страницу и продолжить
        if res is None:
            print(f"[{name}] [WARN] could not fetch page {page} after retries — skipping page")
            time.sleep(1)
            continue
        # [] = пустая страница или 404 => конец пагинации
        if res == []:
            print(f"[{name}] no jokes on page {page} (likely end of pagination) -> stop")
            break

        new = 0
        for j in res:
            if j not in seen:
                seen.add(j)
                all_jokes.append(j)
                new += 1
        print(f"[{name}] page {page}: found {len(res)} jokes, {new} new unique")
        time.sleep(0.35)

    print(f"[{name}] finished: {len(all_jokes)} unique jokes collected")
    return all_jokes


def main():
    start = datetime.utcnow()
    all_rows = []
    seen_global = set()
    saved_files = []

    for name, base in CATEGORIES.items():
        jokes = parse_category(name, base)
        if jokes:
            fname = os.path.join(OUTDIR, f"anekdots_{name}.xlsx")
            pd.DataFrame(jokes, columns=["Анекдот"]).to_excel(fname, index=False, header=False)
            saved_files.append(fname)
            print(f"[{name}] saved {len(jokes)} -> {fname}")
        else:
            print(f"[{name}] no jokes saved")

        for j in jokes:
            if j not in seen_global:
                seen_global.add(j)
                all_rows.append({"Анекдот": j, "Категория": name})

    # итоговый общий файл
    df_all = pd.DataFrame(all_rows)
    if not df_all.empty:
        df_all = df_all.sample(frac=1, random_state=42).reset_index(drop=True)
        all_fname = os.path.join(OUTDIR, "anekdots_all.xlsx")
        df_all.to_excel(all_fname, index=False)
        saved_files.append(all_fname)
        print(f"[ALL] saved combined {len(df_all)} -> {all_fname}")
    else:
        print("[ALL] no rows to save")

    # показ сохранённых файлов
    print("Saved files:")
    for f in saved_files:
        try:
            size = os.path.getsize(f)
        except Exception:
            size = -1
        print(f"  - {f} size={size}")

    if not saved_files:
        print("[ERROR] No files saved at all!", file=sys.stderr)
        sys.exit(2)

    end = datetime.utcnow()
    print(f"Completed in {(end - start).total_seconds():.1f} seconds")


if __name__ == "__main__":
    main()
