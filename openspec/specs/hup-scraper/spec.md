## ADDED Requirements

### Requirement: HUP.hu fórum scraping
The system SHALL scrape HUP.hu fórum topics related to IT layoffs, hiring freezes, and job market concerns using stdlib-only HTTP + HTML parsing.

#### Scenario: Scrape HUP.hu IT topics
- **WHEN** the scraper runs
- **THEN** it SHALL fetch relevant HUP.hu fórum pages using urllib and parse them with html.parser
- **THEN** it SHALL extract post title, date, author, URL, and body text
- **THEN** it SHALL return posts in the same dict format as Reddit posts (id, title, date, created_utc, score, num_comments, url, selftext, subreddit→source)

### Requirement: HUP search queries
The system SHALL search HUP.hu for IT layoff related topics using keyword-based URL filtering or site search.

#### Scenario: Relevant HUP topics found
- **WHEN** HUP.hu has topics matching layoff/leépítés/álláspiac keywords
- **THEN** the scraper SHALL collect them with the same deduplication logic as Reddit (by post id)

#### Scenario: HUP.hu is unreachable
- **WHEN** HUP.hu returns an error or times out
- **THEN** the scraper SHALL log a warning and continue with Reddit-only results (graceful degradation)

### Requirement: Rate limiting for HUP
The system SHALL respect HUP.hu with at least 2 second delays between requests, matching the Reddit scraper behavior.

#### Scenario: Multiple HUP pages fetched
- **WHEN** scraping multiple HUP pages
- **THEN** there SHALL be at least 2 seconds between each HTTP request
