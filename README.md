# India OTT Platform Content Strategy Analysis

The Indian streaming space is genuinely crowded right now — Hotstar,
JioCinema, Amazon Prime, SonyLIV are all fighting for the same eyeballs
with pretty different content bets. I wanted to actually look at the data
instead of going off vibes, so I scraped and analyzed 1,800+ titles across
4 platforms to see who's really betting on what.

## The question I was trying to answer

Which platform has the best content strategy, and what does their
catalogue actually tell you about who they're building for?

## The interesting thing I found

JioHotstar and JioCinema are, content-wise, the exact same platform.
Every single title on one is also on the other — 447 out of 447, zero
exceptions. They're marketed like two different services, but there's no
actual difference in what you get. Makes sense once you remember Jio and
Disney's streaming businesses merged in India, but I wasn't expecting the
overlap to be literally 100%.

## What I actually did

1. Scraped title listings off JustWatch India for all 4 platforms
   (Python, requests, BeautifulSoup) — title, genre, IMDb rating, runtime,
   age rating, production country.
2. Merged everything into one raw dataset and cleaned it up in pandas —
   deduped, filled in the gaps I could, and estimated language since
   JustWatch doesn't actually expose that field directly.
3. Answered a set of real questions about each platform's catalogue:
   how big it is, how fresh it is, how it splits by genre and language,
   how much of it overlaps with the other platforms, and what it'd
   roughly cost you per well-rated title.
4. Built a 4-page Power BI dashboard so the findings are actually visual
   and explorable, not just numbers in a notebook.

## Honest caveats

- **Language** isn't a field JustWatch gives you directly, so I estimated
  it from content origin + genre tags (e.g. "Bollywood" genre → probably
  Hindi). It's a reasonable guess, not verified ground truth — I wouldn't
  treat the regional-language split as precise.
- I aimed for 5,000+ titles going in, but JustWatch India's actual
  per-platform catalogues are just smaller than that in practice — landed
  at 1,807 rows / 1,235 unique titles. That's a real finding about how
  big these catalogues actually are, not a shortcut on my end.
- About 18% of titles don't have an IMDb rating on JustWatch. I left
  those out of anything rating-based rather than guessing a number.

## What's in this repo

```
india-ott-analysis/
├── data/
│   ├── raw_justwatch.csv       # the untouched scrape output
│   ├── raw_listings.csv
│   ├── raw_details.csv
│   ├── cleaned_master.csv      # what I actually analyzed
│   └── summaries/              # one CSV per analysis question, feeds Power BI
├── my_scripts/
│   ├── scrape_listings.py      # stage 1: find every title + its URL
│   ├── scrape_details.py       # stage 2: visit each title, pull the details
│   └── merge_raw.py            # combine both into raw_justwatch.csv
├── notebooks/
│   └── cleaning_and_analysis.ipynb
└── India_OTT_Content_Strategy_Dashboard.pbix
```

## Built with
Python (requests, BeautifulSoup, pandas), Jupyter, Power BI.