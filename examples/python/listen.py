"""Run a batch of X searches and print the posts from the last 36 hours worth reading."""
import datetime as dt
import json
import os
from collections import Counter
from pathlib import Path

from apify_client import ApifyClient

ACTOR = "delicious_zebu/ultimate-x-twitter-advanced-search-scraper"
MY_HANDLE = "your_handle"      # lowercase, without @, so your own posts are skipped
SEEN_FILE = Path("seen.json")  # posts you've already looked at
QUERIES = [  # swap in the topics your buyers talk about
    "apify",
    '"google maps" (scrape OR scraper OR scraping OR leads)',
    '(mcp OR "mcp server") (scraping OR "web data")',
    '"claude code" (scrape OR scraping OR leads)',
]

now = dt.datetime.now(dt.timezone.utc)
since = now - dt.timedelta(hours=36)
run_input = {
    "searchTerms": QUERIES,
    "startDate": since.date().isoformat(),
    "sortBy": "Top",
    "maxItems": 20,  # per query
    "language": "en",
}

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor(ACTOR).call(run_input=run_input)
if run is None:
    raise SystemExit("The run could not be started.")
posts = list(client.dataset(run.default_dataset_id).iterate_items())

seen = set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()
per_author, cards, shortlist = Counter(), set(), []
for post in sorted(posts, key=lambda p: p["viewCount"], reverse=True):
    author = post["authorHandle"].lower()
    if (
        post["tweetId"] in seen  # matched two queries, or came back from an earlier run
        or author == MY_HANDLE
        or dt.datetime.fromisoformat(post["createdAt"]) < since
        or per_author[author] == 2  # one busy account can fill a query on its own
        or post["cardTitle"] in cards  # the same video or article, shared by many accounts
    ):
        continue
    seen.add(post["tweetId"])
    per_author[author] += 1
    if post["cardTitle"]:
        cards.add(post["cardTitle"])
    shortlist.append(post)
    if len(shortlist) == 15:
        break

SEEN_FILE.write_text(json.dumps(sorted(seen)))
print(f"{len(posts)} posts found, {len(shortlist)} on the shortlist")
for post in shortlist:
    hours = (now - dt.datetime.fromisoformat(post["createdAt"])).total_seconds() / 3600
    print(f'{post["viewCount"]:>7,} views {post["replyCount"]:>3} replies {hours:>3.0f}h ago  {post["tweetUrl"]}')
    print(f'{"":>38}{post["queryStr"]}')
