## ADDED Requirements

### Requirement: Google News RSS query configuration
The system SHALL define a `GNEWS_QUERIES` list containing search queries for Google News RSS.

The queries SHALL include:
- Magyar IT leépítési query-k: `leépítés IT`, `elbocsátás programozó`, `leépítés informatikus`
- AI/munkahely query-k: `mesterséges intelligencia munkahely`, `AI leépítés`
- Angol query-k magyar kontextussal: `tech layoff Hungary`, `AI jobs Budapest`
- Hiring freeze: `hiring freeze Magyarország`
- Cégspecifikus: `Ericsson leépítés`, `Audi leépítés`, `Continental leépítés`, `OTP leépítés`

#### Scenario: Query list is complete
- **WHEN** the scraper is initialized
- **THEN** `GNEWS_QUERIES` SHALL contain at least 10 search queries covering IT layoffs, AI job impact, and company-specific searches

### Requirement: RSS fetch and parse
The system SHALL fetch Google News RSS search results from `https://news.google.com/rss/search?q=QUERY&hl=hu&gl=HU&ceid=HU:hu` and parse the XML response using `xml.etree.ElementTree`.

#### Scenario: Successful RSS fetch
- **WHEN** a query is executed against the Google News RSS endpoint
- **THEN** the system SHALL parse each `<item>` element extracting `<title>`, `<link>`, `<pubDate>`, and `<source>` text

#### Scenario: RSS fetch failure
- **WHEN** the HTTP request fails (network error, 429, 403, etc.)
- **THEN** the system SHALL log a warning and skip to the next query without crashing

#### Scenario: Malformed XML
- **WHEN** the response is not valid XML
- **THEN** the system SHALL log a warning and skip to the next query

### Requirement: Post normalization
The system SHALL normalize each RSS item into the standard post dict format used by the pipeline.

Fields:
- `id`: `gnews-` prefix + first 10 chars of SHA256 hash of (title + date)
- `title`: from `<title>` element
- `subreddit`: literal string `"google-news"`
- `source`: literal string `"google-news"`
- `news_source`: from `<source>` element text (e.g. "Portfolio.hu")
- `date`: parsed from `<pubDate>` in `YYYY-MM-DD` format
- `created_utc`: Unix timestamp from `<pubDate>`
- `score`: `0`
- `num_comments`: `0`
- `url`: from `<link>` element (Google redirect URL)
- `selftext`: empty string
- `top_comments`: empty list

#### Scenario: Standard RSS item
- **WHEN** an RSS item has title "Leépítés jön a győri Audinál", source "Portfolio.hu", pubDate "Wed, 14 Jan 2026 08:00:00 GMT"
- **THEN** the post dict SHALL have `source="google-news"`, `news_source="Portfolio.hu"`, `date="2026-01-14"`, and a deterministic `id` starting with `gnews-`

#### Scenario: Missing source element
- **WHEN** an RSS item has no `<source>` element
- **THEN** `news_source` SHALL default to `"unknown"`

### Requirement: Deduplication within Google News results
The system SHALL deduplicate results across queries using the post `id` as key.

#### Scenario: Same article from different queries
- **WHEN** the same article appears in results for both "leépítés IT" and "Audi leépítés"
- **THEN** the system SHALL keep only one copy (first seen)

### Requirement: Rate limiting
The system SHALL wait at least `REQUEST_DELAY` seconds between HTTP requests to Google News RSS.

#### Scenario: Multiple queries
- **WHEN** executing 10+ queries sequentially
- **THEN** each request SHALL be separated by at least `REQUEST_DELAY` seconds

### Requirement: run_google_news_scraper function
The system SHALL provide a `run_google_news_scraper()` function that returns `dict[str, dict]` (id → post), matching the pattern of `run_reddit_scraper()` and `run_hup_scraper()`.

#### Scenario: Integration with run_scraper
- **WHEN** `run_scraper()` is called
- **THEN** it SHALL call `run_google_news_scraper()` and merge results alongside Reddit and HUP results

### Requirement: pubDate parsing
The system SHALL parse RFC 2822 date strings from `<pubDate>` using `email.utils.parsedate_to_datetime` from stdlib.

#### Scenario: Standard pubDate
- **WHEN** pubDate is "Wed, 14 Jan 2026 08:00:00 GMT"
- **THEN** the system SHALL parse it to date "2026-01-14" and corresponding Unix timestamp

#### Scenario: Unparseable date
- **WHEN** pubDate cannot be parsed
- **THEN** the system SHALL fall back to today's date
