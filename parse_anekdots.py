# parse_anekdots.py (verbosed)
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
    # (вставь сюда весь твой список категорий — как раньше)
    "evreev": "https://shytok.net/anekdots/anekdoty-pro-evreev",
    "advokatov": "https://shytok.net/anekdots/anekdoty-pro-advokatov",
    "armyan": "https://shytok.net/anekdots/anekdoty-pro-armyan",
    "voennyih": "https://shytok.net/anekdots/anekdoty-pro-voennyih",
    "zhivotnyh": "https://shytok.net/anekdots/anekdoty-pro-zhivotnyh",
    # ... остальные категории ...
}

OUTDIR = "output"
os.makedirs(OUTDIR, exist_ok=True)

def build_url(base, page):
    if page == 1:
        return f"{base}.html"
    return f"{base}-{page}.html"

def parse_page(url):
    try:
        resp = requests.get(url, timeout=12, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] request {url}: {e}", file=sys.stderr)
        return None  # None = ошибка, [] = пустая страница
    soup = BeautifulSoup(resp.text, "html.parser")
    blocks = soup.find_all("div", class_="text2")
    jokes = []
    for b in blocks:
        text = b.get_text("\n", strip=True)
        if text and len(text) > 3:
            jokes.append(text)
    return jokes

def parse_category(name, base_url, max_pages=200):
    print(f"[{name}] start parsing")
    all_jokes = []
    seen = set()
    for page in range(1, max_pages + 1):
        url = build_url(base_url, page)
        print(f"[{name}] page {page} -> {url}")
        res = parse_page(url)
        if res is None:
            print(f"[{name}] ERROR loading page {page}, skipping page and continuing")
            time.sleep(1)
            continue
        if not res:
            print(f"[{name}] no jokes on page {page} -> stopping pagination")
            break
        new = 0
        for j in res:
            if j not in seen:
                seen.add(j)
                all_jokes.append(j)
                new += 1
        print(f"[{name}] page {page}: found {len(res)} jokes, {new} new unique")
        time.sleep(0.4)
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
            filename = os.path.join(OUTDIR, f"anekdots_{name}.xlsx")
            pd.DataFrame(jokes, columns=["Анекдот"]).to_excel(filename, index=False, header=False)
            saved_files.append(filename)
            print(f"[{name}] saved {len(jokes)} -> {filename}")
        else:
            print(f"[{name}] no jokes saved")

        for j in jokes:
            if j not in seen_global:
                seen_global.add(j)
                all_rows.append({"Анекдот": j, "Категория": name})

    # итог
    df_all = pd.DataFrame(all_rows)
    # перемешиваем итог для стабильности (можно убрать random_state для нового порядка)
    if not df_all.empty:
        df_all = df_all.sample(frac=1, random_state=42).reset_index(drop=True)
        all_fname = os.path.join(OUTDIR, "anekdots_all.xlsx")
        df_all.to_excel(all_fname, index=False)
        saved_files.append(all_fname)
        print(f"[ALL] saved combined {len(df_all)} -> {all_fname}")
    else:
        print("[ALL] no rows to save")

    end = datetime.utcnow()
    print("Summary:")
    print(f"  Time: {start.isoformat()} -> {end.isoformat()}")
    print(f"  Category files saved: {len([f for f in saved_files if 'anekdots_' in f])}")
    print("Saved files:")
    for f in saved_files:
        try:
            size = os.path.getsize(f)
        except Exception:
            size = -1
        print(f"  - {f}  size={size}")
    # exit nonzero if no files at all (makes workflow fail visibly)
    if not saved_files:
        print("[ERROR] No files saved at all!", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
