"""
Stage 1: Scrape title listings from JustWatch India per platform.
Collects: title, url, platform, content_type (movie/show)
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import random

PLATFORMS = {
    "JioHotstar": "jiohotstar",
    "JioCinema": "jio-cinema",
    "Amazon Prime Video": "amazon-prime-video",
    "SonyLIV": "sony-liv",
}

CONTENT_TYPES = {
    "movie": "movies",
    "show": "tv-shows",
}

BASE_URL = "https://www.justwatch.com/in/provider/{slug}/{type_path}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MAX_PAGES_PER_CATEGORY = 100
REQUEST_DELAY = (1.5, 3.0)


def scrape_listing_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"  [!] status {resp.status_code} for {url}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    for a in soup.select('a[href*="/movie/"], a[href*="/tv-show/"]'):
        href = a.get("href", "")
        if "/movie/" not in href and "/tv-show/" not in href:
            continue
        img = a.find("img")
        if not img or not img.get("alt"):
            continue
        title = img.get("alt").strip()
        full_url = href if href.startswith("http") else f"https://www.justwatch.com{href}"
        results.append((title, full_url))

    seen = set()
    deduped = []
    for title, url_ in results:
        if url_ not in seen:
            seen.add(url_)
            deduped.append((title, url_))
    return deduped


def scrape_platform_type(platform_name, slug, content_type, type_path):
    print(f"\n== {platform_name} / {content_type} ==")
    all_rows = []
    seen_urls = set()

    for page in range(1, MAX_PAGES_PER_CATEGORY + 1):
        if page == 1:
            url = BASE_URL.format(slug=slug, type_path=type_path)
        else:
            url = BASE_URL.format(slug=slug, type_path=type_path) + f"?page={page}"

        print(f"  page {page}: {url}")
        page_results = scrape_listing_page(url)

        new_count = 0
        for title, title_url in page_results:
            if title_url not in seen_urls:
                seen_urls.add(title_url)
                all_rows.append({
                    "title": title,
                    "url": title_url,
                    "platform": platform_name,
                    "content_type": content_type,
                })
                new_count += 1

        print(f"    -> {len(page_results)} cards found, {new_count} new")

        if new_count == 0:
            print("    no new titles, stopping pagination for this category")
            break

        time.sleep(random.uniform(*REQUEST_DELAY))

    return all_rows


def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url", "platform", "content_type"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    all_rows = []
    for platform_name, slug in PLATFORMS.items():
        for content_type, type_path in CONTENT_TYPES.items():
            rows = scrape_platform_type(platform_name, slug, content_type, type_path)
            all_rows.extend(rows)
            save_csv(all_rows, "data/raw_listings.csv")

    print(f"\nDone. {len(all_rows)} total rows saved.")


if __name__ == "__main__":
    main()