# Twitter Scraper — export tweets from X advanced search with views, likes and author stats

This Twitter advanced search scraper exports posts from X (Twitter) searches by keyword, hashtag, account, engagement and date range, with view and like counts, media links and author stats for every post. Run it in Apify Console without code and export CSV or Excel, or call it from curl, Python or Node.js. No X account needed.

[Run it on Apify](https://apify.com/delicious_zebu/ultimate-x-twitter-advanced-search-scraper?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper) · [API reference](https://apify.com/delicious_zebu/ultimate-x-twitter-advanced-search-scraper/api?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper)

## What you get

Each row is one post. The coverage column comes from one of our runs: 11 English searches on Oct 7, 2026, 75 posts. Your numbers will vary by search.

| Field | What it is | Filled in our sample |
| --- | --- | --- |
| `fullText` | The post's text | 100% |
| `createdAt` | When it was posted, in UTC | 100% |
| `tweetUrl` | Link to the post on x.com | 100% |
| `viewCount` | Views | 96% |
| `likeCount`, `replyCount`, `repostCount`, `quoteCount`, `bookmarkCount` | Engagement counts. `repostCount` is retweets plus quotes | Every row (0 when there are none) |
| `authorHandle`, `authorName`, `authorFollowers` | Who posted it, and how many followers they have | 100% |
| `authorBio`, `authorLocation`, `authorWebsite` | The author's profile details | 88%, 67%, 59% |
| `imageUrls`, `videoUrls` | Photos and videos in the post | 27%, 8% |
| `externalUrls`, `mentions`, `hashtags` | Links, accounts and hashtags in the post | 41%, 37%, 12% |
| `isReply`, `isQuote`, `quotedText` | Whether it's a reply or a quote, and the quoted post's text | Flags in every row; `quotedText` 11% |
| `queryStr` | Which of your searches found the post | 100% |

Each row also has the author's following, post and media counts, account creation date and profile image, plus the post's language, conversation ID, reply target, link card and `searchUrl`, the x.com search that found it: 55 fields in all.

Three things to know before you use the data:

- **Top without a date range means top posts of all time.** Our quick-start search below has no dates, and it returned posts from 2022 to 2026. Set `startDate` (and `endDate`) when you want recent posts.
- **Older posts can show 0 views.** In that test, a 2022 post with 721 likes had a `viewCount` of 0, because X doesn't show view counts for posts that old.
- **Batch searches can overlap.** One post can match more than one of your search terms. Dedupe on `tweetId`; the Python examples do.

## Quick start

### No code (Apify Console)

1. Go to the [scraper's page on Apify](https://apify.com/delicious_zebu/ultimate-x-twitter-advanced-search-scraper?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper) and open it in Apify Console. You'll be asked to sign in or create an account.
2. Enter one or more **Search terms**, one search per line. X's search operators work, such as quotes for an exact phrase and `OR`. Optionally set a **Start date**, and set **Max items**, which applies to each search.
3. Click **Start**. When the run finishes, click **Export** and choose CSV or Excel.

### API

Copy your API token from [Apify Console → Settings → API & Integrations](https://console.apify.com/settings/integrations) and set it as an environment variable:

```bash
export APIFY_TOKEN="<your Apify API token>"
```

**curl** runs the scraper and saves the results as a CSV file:

```bash
curl -X POST "https://api.apify.com/v2/acts/delicious_zebu~ultimate-x-twitter-advanced-search-scraper/run-sync-get-dataset-items?format=csv" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"searchTerms": ["\"web scraping\" python"], "sortBy": "Top", "maxItems": 20, "language": "en"}' \
  -o tweets.csv
```

Remove `format=csv` to get JSON, or use `format=xlsx` for Excel. The CSV puts list fields such as media links into their own columns (56 columns in our test). This call waits for the run to finish, so use it for small jobs and the clients below for bigger ones.

**Python** ([examples/python/search.py](examples/python/search.py)) needs Python 3.11+ and apify-client 3.x: run `pip install -r examples/python/requirements.txt`, then `python examples/python/search.py`. It saves one row per post to `tweets.csv`.

```python
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
```

**Node.js** ([examples/node/run.mjs](examples/node/run.mjs)): run `cd examples/node && npm install && node run.mjs`. It prints the posts, most viewed first.

```js
// Search X (Twitter) and print the matching tweets, most viewed first.
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor('delicious_zebu/ultimate-x-twitter-advanced-search-scraper').call({
    searchTerms: ['"web scraping" python'],
    sortBy: 'Top',
    maxItems: 20,
    language: 'en',
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();

items.sort((a, b) => b.viewCount - a.viewCount);
console.table(items.map(({ createdAt, viewCount, likeCount, tweetUrl }) => ({ createdAt, viewCount, likeCount, tweetUrl })));
```

## Daily social listening

[examples/python/listen.py](examples/python/listen.py) runs a batch of searches once a day and prints a short list of posts worth reading, most viewed first. It skips posts you've already seen (it keeps their IDs in `seen.json`), your own posts, anything older than 36 hours, more than two posts from the same account, and repeats of the same shared link. Swap in the topics your buyers talk about and run it from cron.

```python
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
```

We use this ourselves to find X posts where we can help. The write-up, with numbers from our own daily runs and what we learned about writing replies, is on our blog: [Find X posts worth replying to, every day](https://zebudata.hashnode.dev/x-twitter-social-listening-advanced-search). Write replies by hand: X's automation rules don't allow automated replies based on keyword searches alone.

## Example input

The input from the quick-start test:

```json
{
  "searchTerms": ["\"web scraping\" python"],
  "sortBy": "Top",
  "maxItems": 20,
  "language": "en"
}
```

| Field | Type | What it does |
| --- | --- | --- |
| `searchTerms` | list of strings | One search per line. Each runs on its own and is combined with the fields below. X operators such as quotes and `OR` work. |
| `startDate`, `endDate` | strings (`YYYY-MM-DD`) | Optional date range, both days included. Leave empty to search all time. |
| `sortBy` | string | `Top` (X's ranking, stable results) or `Latest` (every post, newest first). Default: `Top`. |
| `maxItems` | integer | Posts to collect for each search. Default: 80. `0` means no limit. |
| `language` | string | Only posts in this language, for example `en`. Default: `any`. |
| `From_these_accounts`, `Mentioning_these_accounts` | strings | Handles without @, separated by spaces. |
| `Minimum_likes`, `Minimum_replies`, `Minimum_reposts` | integers | Skip posts below these counts. |
| `excludeReplies` | boolean | Keep standalone posts only. |
| `searchUrls` | list of strings | x.com search URLs, run exactly as they are, including their operators, dates and Top or Latest tab. |

## Example output

One real row from the quick-start test, a post by LangChain's company account. The text is cut after its first line, and some fields are left out.

```json
{
  "tweetId": "1784590140444176592",
  "tweetUrl": "https://x.com/LangChain/status/1784590140444176592",
  "createdAt": "2024-04-28 14:27:00+00:00",
  "fullText": "🕷️ ScrapeGraphAI: You Only Scrape Once …",
  "language": "en",
  "imageUrls": [
    "https://pbs.twimg.com/media/GMNjBn0bcAAyX7K.jpg"
  ],
  "replyCount": 22,
  "repostCount": 243,
  "retweetCount": 231,
  "quoteCount": 12,
  "likeCount": 1157,
  "viewCount": 123074,
  "bookmarkCount": 1702,
  "isReply": false,
  "isQuote": false,
  "authorName": "LangChain",
  "authorHandle": "LangChain",
  "authorFollowers": 269268,
  "isVerified": true,
  "verifiedType": "Business",
  "queryStr": "\"web scraping\" python"
}
```

## Use cases

- **Social listening:** find posts where people ask about the problem your product solves, and reply by hand. See [Daily social listening](#daily-social-listening).
- **Brand and competitor monitoring:** track mentions of a brand or product over a date range, or every post from a set of accounts with `From_these_accounts`.
- **Research datasets:** export the posts on a topic, in one language and date range, for sentiment or topic analysis.
- **Creator discovery:** sort by `viewCount` or `likeCount` and check `authorFollowers` and `verifiedType` to find the accounts that drive a conversation.

## Use it from AI agents (MCP)

Add a URL below to any MCP client that supports remote (streamable HTTP) servers.

Just this scraper:

```
https://mcp.apify.com/?tools=delicious_zebu/ultimate-x-twitter-advanced-search-scraper
```

Our X (Twitter), YouTube & TikTok bundle, listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/) as `io.github.zebudata/social-video-data`. It adds our X profile and X trends scrapers, three YouTube scrapers and a TikTok comments scraper:

```
https://mcp.apify.com/?tools=delicious_zebu/ultimate-x-twitter-advanced-search-scraper,delicious_zebu/advanced-x-twitter-profile-scraper,delicious_zebu/x-global-trending-scraper,delicious_zebu/youtube-video-scraper-by-keyword,delicious_zebu/youtube-video-data-scraper,delicious_zebu/youtube-comments-replies-scraper,delicious_zebu/tiktok-video-comment-scraper
```

In Claude Code:

```bash
claude mcp add --transport http x-search "https://mcp.apify.com/?tools=delicious_zebu/ultimate-x-twitter-advanced-search-scraper"
```

The first time a tool runs, you sign in to Apify; usage is billed to your Apify account.

## FAQ

### How much does it cost?

It's pay per event: you're charged when a run starts and for each post in the dataset. See the [Pricing tab](https://apify.com/delicious_zebu/ultimate-x-twitter-advanced-search-scraper/pricing?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper) for current rates. Start with a small `maxItems` to see what a search returns before you scale up.

### Do I need an X account or the X API?

No. It collects public X search results, so you don't need an X account, a login or X API keys. You only need an Apify account to run it.

### How many posts can I get per run?

`maxItems` sets the limit for each search (default 80, and `0` means no limit), and `searchTerms` takes a list, so one run can cover many searches. For a date range, `splitMode` splits it by day (the default and the most thorough), week or month.

### What's the difference between Top and Latest?

`Top` returns the posts X ranks as most relevant, and its results are stable, so they're easy to check against x.com. `Latest` returns every post, newest first: more complete, but the order keeps changing as new posts arrive. For search URLs, the tab in the URL decides.

### Can I use X's advanced search operators?

Yes. Search terms accept X's operators, such as quotes for an exact phrase and `OR`. For account, engagement, media, language, verified and location filters, use the matching input fields; they're added to every search term. You can also paste x.com search URLs into `searchUrls`, and they run exactly as they are.

### Can I use the data for outreach or automated replies?

The scraper collects public posts. You're responsible for using the data in line with applicable laws (for example GDPR) and X's terms. Don't automate replies: X's automation rules don't allow automated replies based on keyword searches alone.

## Related scrapers

- [Twitter Profile Scraper - All X Tweets by Date Range](https://apify.com/delicious_zebu/advanced-x-twitter-profile-scraper?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper)
- [Twitter Trends Scraper - X Global Trending](https://apify.com/delicious_zebu/x-global-trending-scraper?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper)
- [All Zebu Data scrapers on Apify](https://apify.com/delicious_zebu?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper)

## Support

Found a problem or need a field? Open an issue on the scraper's [Issues tab](https://apify.com/delicious_zebu/ultimate-x-twitter-advanced-search-scraper/issues/open?utm_source=github&utm_medium=readme&utm_campaign=ultimate-x-twitter-advanced-search-scraper) on Apify.

Zebu Data is an independent developer on Apify Store, not affiliated with or endorsed by X Corp.
