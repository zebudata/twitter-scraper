"""Search X (Twitter) and save the matching tweets to tweets.csv."""
import csv
import os

from apify_client import ApifyClient

ACTOR = "delicious_zebu/ultimate-x-twitter-advanced-search-scraper"
COLUMNS = ["createdAt", "tweetUrl", "fullText", "viewCount", "likeCount", "replyCount",
           "authorHandle", "authorFollowers", "queryStr"]

run_input = {
    "searchTerms": ['"web scraping" python'],
    "sortBy": "Top",
    "maxItems": 20,  # per search term
    "language": "en",
}

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor(ACTOR).call(run_input=run_input)
if run is None:
    raise SystemExit("The run could not be started.")

seen = set()
with open("tweets.csv", "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig opens cleanly in Excel
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for item in client.dataset(run.default_dataset_id).iterate_items():
        # With several search terms, the same tweet can match more than one: keep one row per tweet.
        if item["tweetId"] in seen:
            continue
        seen.add(item["tweetId"])
        writer.writerow({column: item.get(column, "") for column in COLUMNS})

print(f"Saved {len(seen)} tweets to tweets.csv")
