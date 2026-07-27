"""
Stage 2: Visit each title's JustWatch page and extract genre, IMDb rating,
production country, runtime, age rating.
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

REQUEST_DELAY = (0.7, 1.5)
CHECKPOINT_EVERY = 25

INPUT_PATH = "data/raw_listings.csv"
OUTPUT_PATH = "data/raw_details.csv"

FIELDNAMES = [
    "url", "imdb_rating", "imdb_votes", "genres",
    "production_country", "runtime_min", "age_rating", "release_year",
]


def load_already_scraped(path):
    if not os.path.exists(path):
        return set()
    seen = set()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            seen.add(row["url"])
    return seen


def parse_title_page(html):
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="|")

    data = {
        "imdb_rating": None, "imdb_votes": None, "genres": None,
        "production_country": None, "runtime_min": None,
        "age_rating": None, "release_year": None,
    }

    h1 = soup.find("h1")
    if h1:
        m = re.search(r"\((\d{4})\)", h1.get_text())
        if m:
            data["release_year"] = int(m.group(1))

    # IMDb rating looks like "8.3  (143k)" -- note the double space before the parenthesis
    m = re.search(r"(\d\.\d)\s{2,}\((\d+(?:\.\d+)?k?)\)", text)
    if m:
        data["imdb_rating"] = float(m.group(1))
        data["imdb_votes"] = m.group(2)

    # Genres sit between "Genres|" and "|Runtime"
    m = re.search(r"Genres\|(.*?)\|Runtime", text)
    if m:
        parts = [p.strip(", ").strip() for p in m.group(1).split("|") if p.strip(", ").strip()]
        data["genres"] = ", ".join(parts)

    # Runtime sits between "Runtime|" and "|Age rating"
    m = re.search(r"Runtime\|([^|]+)\|Age rating", text)
    if m:
        runtime_text = m.group(1)
        hours = re.search(r"(\d+)h", runtime_text)
        mins = re.search(r"(\d+)min", runtime_text)
        total = (int(hours.group(1)) * 60 if hours else 0) + (int(mins.group(1)) if mins else 0)
        data["runtime_min"] = total if total else None

    # Age rating sits between "Age rating|" and "|Production country"
    m = re.search(r"Age rating\|([^|]+)\|Production country", text)
    if m:
        data["age_rating"] = m.group(1).strip()

    # Production country comes right after "Production country|"
    m = re.search(r"Production country\|([^|]+)", text)
    if m:
        data["production_country"] = m.group(1).strip()

    return data
def main():
    if not os.path.exists(INPUT_PATH):
        print(f"Missing {INPUT_PATH} -- run scrape_listings.py first.")
        return

    with open(INPUT_PATH, newline="", encoding="utf-8") as f:
        listing_rows = list(csv.DictReader(f))

    unique_urls = sorted({row["url"] for row in listing_rows})
    already = load_already_scraped(OUTPUT_PATH)
    todo = [u for u in unique_urls if u not in already]

    print(f"{len(unique_urls)} unique titles total, {len(already)} already scraped, "
          f"{len(todo)} remaining.")

    write_header = not os.path.exists(OUTPUT_PATH)
    out_f = open(OUTPUT_PATH, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    if write_header:
        writer.writeheader()

    count_since_flush = 0
    try:
        for i, url in enumerate(todo, 1):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    print(f"[{i}/{len(todo)}] status {resp.status_code}: {url}")
                    row = {"url": url}
                    for k in FIELDNAMES:
                        row.setdefault(k, None)
                    writer.writerow(row)
                    continue

                parsed = parse_title_page(resp.text)
                parsed["url"] = url
                writer.writerow(parsed)

                if i % 10 == 0 or i == 1:
                    print(f"[{i}/{len(todo)}] {url} -> "
                          f"IMDb {parsed['imdb_rating']}, genres: {parsed['genres']}")

            except requests.RequestException as e:
                print(f"[{i}/{len(todo)}] request failed for {url}: {e}")
                row = {"url": url}
                for k in FIELDNAMES:
                    row.setdefault(k, None)
                writer.writerow(row)

            count_since_flush += 1
            if count_since_flush >= CHECKPOINT_EVERY:
                out_f.flush()
                count_since_flush = 0

            time.sleep(random.uniform(*REQUEST_DELAY))

    except KeyboardInterrupt:
        print("\nInterrupted -- progress saved. Re-run the script to resume.")
    finally:
        out_f.close()

    print("Done.")


if __name__ == "__main__":
    main()