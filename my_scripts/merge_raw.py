"""
Merge raw_listings.csv + raw_details.csv into the single raw_justwatch.csv
required by the project spec.
"""

import pandas as pd

listings = pd.read_csv("data/raw_listings.csv")
details = pd.read_csv("data/raw_details.csv")

merged = listings.merge(details, on="url", how="left")

merged["content_origin"] = merged["production_country"].apply(
    lambda c: "Indian" if isinstance(c, str) and "india" in c.lower() else
              ("International" if pd.notna(c) else None)
)

merged = merged.rename(columns={
    "content_type": "type",
    "genres": "genre",
})

final_cols = [
    "title", "type", "genre", "release_year", "imdb_rating", "imdb_votes",
    "platform", "content_origin", "production_country",
    "runtime_min", "age_rating", "url",
]
merged = merged[[c for c in final_cols if c in merged.columns]]

merged.to_csv("data/raw_justwatch.csv", index=False)

print(f"Saved {len(merged)} rows to data/raw_justwatch.csv")
print(f"\nMissing imdb_rating: {merged['imdb_rating'].isna().sum()} rows")
print(f"Missing genre: {merged['genre'].isna().sum()} rows")
print(f"\nRows per platform:")
print(merged['platform'].value_counts())