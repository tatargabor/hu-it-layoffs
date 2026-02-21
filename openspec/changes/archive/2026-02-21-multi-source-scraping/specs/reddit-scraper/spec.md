## MODIFIED Requirements

### Requirement: Reddit subreddit configuration
The scraper SHALL search the following subreddits with appropriate queries:

- **r/programmingHungary**: Current full query set (unchanged)
- **r/hungary**: Expanded queries including álláskereső, álláspiac, hiring freeze, and company names (Ericsson, Continental, OTP, NNG, Lensa, Microsoft)
- **r/layoffs**: Global layoff subreddit filtered with "Hungary OR Hungarian OR Budapest" queries
- **r/cscareerquestions**: Global CS career subreddit filtered with "Hungary OR Hungarian OR Budapest" queries

#### Scenario: r/hungary expanded queries
- **WHEN** the scraper searches r/hungary
- **THEN** it SHALL include queries for: álláskereső OR álláspiac, hiring freeze, Ericsson OR Continental OR OTP OR NNG OR Lensa OR Microsoft leépítés, in addition to the existing queries

#### Scenario: r/layoffs Hungary filter
- **WHEN** the scraper searches r/layoffs
- **THEN** it SHALL search for "Hungary OR Hungarian OR Budapest" to find globally reported Hungarian layoffs

#### Scenario: r/cscareerquestions Hungary filter
- **WHEN** the scraper searches r/cscareerquestions
- **THEN** it SHALL search for "Hungary OR Hungarian OR Budapest" to find career questions about Hungarian IT market

### Requirement: Noise reduction
The scraper SHALL reduce false positives from overly broad queries.

#### Scenario: Narrowed munkanélküli query
- **WHEN** searching with the `munkanélküli OR nincs munka` query
- **THEN** it SHALL be narrowed to `munkanélküli IT OR nincs munka programozó OR nincs munka fejlesztő` to reduce irrelevant results

### Requirement: Source field for Reddit posts
Each Reddit post SHALL include `source: "reddit"` in its dict.

#### Scenario: Reddit post includes source
- **WHEN** a post is scraped from any Reddit subreddit
- **THEN** the post dict SHALL contain `"source": "reddit"`
