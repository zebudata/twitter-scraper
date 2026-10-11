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
