## ADDED Requirements

### Requirement: Search multiple subreddits with Hungarian keywords
The scraper SHALL search `r/programmingHungary` and `r/hungary` using the `old.reddit.com` JSON search API without authentication. It SHALL execute multiple keyword queries per subreddit to maximize coverage.

Keywords SHALL include at minimum:
- Hungarian: `elbocsátás`, `leépítés`, `kirúgás`, `létszámcsökkentés`, `bújtatott leépítés`, `quiet firing`
- English: `layoff`, `fired`, `hiring freeze`
- Combined: `AI elveszi`, `AI munka`, `álláskereső`, `álláspiac`
- Company-specific: known affected company names from previous scrapes

#### Scenario: Basic multi-keyword search
- **WHEN** scraper runs with default configuration
- **THEN** it SHALL execute at least 8 different search queries across both subreddits
- **THEN** results SHALL be deduplicated by post ID

#### Scenario: Hungarian character encoding
- **WHEN** a search query contains Hungarian characters (á, é, í, ó, ö, ő, ú, ü, ű)
- **THEN** characters SHALL be properly URL-encoded via `urllib.parse.quote()`
- **THEN** the API SHALL return valid JSON results

### Requirement: Fetch post details with comments
The scraper SHALL fetch full post details (selftext) and top-level comments for each discovered post using the `old.reddit.com/r/{sub}/comments/{id}.json` endpoint.

#### Scenario: Post detail fetch
- **WHEN** a post ID is discovered from search
- **THEN** scraper SHALL fetch the full selftext and up to 20 top-level comments
- **THEN** both SHALL be stored in the raw output

### Requirement: Rate limiting and resilience
The scraper SHALL wait at least 2.0 seconds between HTTP requests. On HTTP 429 responses, it SHALL wait 10 seconds and retry once.

#### Scenario: Rate limit hit
- **WHEN** Reddit returns HTTP 429
- **THEN** scraper SHALL wait 10 seconds
- **THEN** scraper SHALL retry the request once
- **THEN** if still 429, scraper SHALL skip that request and log a warning

### Requirement: Pagination support
The scraper SHALL use Reddit's `after` parameter to paginate through results when more than 100 posts match a query.

#### Scenario: More than 100 results
- **WHEN** a search returns 100 results (Reddit's max per page)
- **THEN** scraper SHALL fetch the next page using the `after` token
- **THEN** scraper SHALL continue until fewer than 100 results or max 5 pages

### Requirement: Output raw JSON
The scraper SHALL save all collected posts to `data/raw_posts.json` with fields: `id`, `title`, `subreddit`, `date`, `created_utc`, `score`, `num_comments`, `url`, `selftext`, `top_comments[]`.

#### Scenario: Output file format
- **WHEN** scraper completes
- **THEN** `data/raw_posts.json` SHALL contain a JSON array sorted by `created_utc` descending
- **THEN** each post SHALL have all required fields populated
