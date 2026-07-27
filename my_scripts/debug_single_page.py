"""
Fetch one known JustWatch title page and check what parse_title_page()
extracts from it, before we scrape hundreds of pages.
"""

import requests
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from scrape_details import parse_title_page, HEADERS

TEST_URL = "https://www.justwatch.com/in/movie/dhurandhar-2025"


def main():
    print(f"Fetching {TEST_URL} ...")
    resp = requests.get(TEST_URL, headers=HEADERS, timeout=15)
    print(f"Status: {resp.status_code}")

    os.makedirs("data", exist_ok=True)
    with open("data/debug_page.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Raw HTML saved to data/debug_page.html")

    parsed = parse_title_page(resp.text)
    print("\nParsed result:")
    for k, v in parsed.items():
        print(f"  {k}: {v}")

def inspect_raw_text():
    resp = requests.get(TEST_URL, headers=HEADERS, timeout=15)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(separator="|")

    # find where "IMDB" appears and print surrounding context
    idx = text.upper().find("IMDB")
    print("\n--- around IMDB ---")
    print(text[max(0, idx-50):idx+100])

    idx2 = text.upper().find("AGE RATING")
    print("\n--- around AGE RATING ---")
    print(text[max(0, idx2-50):idx2+100])

    idx3 = text.upper().find("GENRE")
    print("\n--- around GENRES ---")
    print(text[max(0, idx3-50):idx3+300])

if __name__ == "__main__":
    main()
    inspect_raw_text()