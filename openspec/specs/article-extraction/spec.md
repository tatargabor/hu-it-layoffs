## ADDED Requirements

### Requirement: Google News URL decoding
The scraper SHALL decode Google News RSS article URLs to real article URLs using the `googlenewsdecoder` library before content extraction.

#### Scenario: Successful URL decode
- **WHEN** a Google News RSS item has a URL like `https://news.google.com/rss/articles/CBMi...`
- **THEN** the scraper SHALL decode it to the real article URL (e.g., `https://www.vg.hu/...`)
- **AND** store the real URL in the post's `url` field (replacing the GN redirect URL)

#### Scenario: URL decode failure
- **WHEN** `googlenewsdecoder` fails to decode a URL
- **THEN** the scraper SHALL keep the original Google News URL
- **AND** leave `selftext` empty (title-only validation as fallback)
- **AND** log a warning

### Requirement: Article content extraction
The scraper SHALL extract article body text from decoded URLs using the `trafilatura` library and store it in the `selftext` field.

#### Scenario: Successful extraction
- **WHEN** a real article URL is available and `trafilatura` extracts text >= 50 characters
- **THEN** the extracted text SHALL be stored in the post's `selftext` field

#### Scenario: Extraction returns insufficient text
- **WHEN** `trafilatura` returns less than 50 characters or None
- **THEN** `selftext` SHALL remain empty
- **AND** the post proceeds with title-only data

#### Scenario: Extraction error or timeout
- **WHEN** fetching or extracting the article fails
- **THEN** the scraper SHALL log a warning and continue to the next post
- **AND** `selftext` SHALL remain empty

### Requirement: Rate limiting for article fetching
The scraper SHALL wait at least 1.5 seconds between `googlenewsdecoder` calls to avoid Google rate limits.

#### Scenario: Sequential article fetching
- **WHEN** processing multiple Google News articles
- **THEN** there SHALL be a minimum 1.5 second delay between decode requests

### Requirement: Re-enable Google News source
`ENABLED_SOURCES` SHALL default to `["reddit", "google-news"]` so Google News is active with full content extraction.

#### Scenario: Default pipeline run
- **WHEN** the pipeline runs with default configuration
- **THEN** both Reddit and Google News scrapers SHALL execute

### Requirement: Backfill existing posts
A standalone script SHALL exist to backfill `selftext` for existing Google News posts that have empty body text.

#### Scenario: Running backfill
- **WHEN** `scripts/backfill_gnews_content.py` is executed
- **THEN** it SHALL load `data/validated_posts.json`
- **AND** for each Google News post with empty `selftext`, decode URL and extract content
- **AND** save the updated posts back to `data/validated_posts.json`
- **AND** report how many posts were successfully backfilled
