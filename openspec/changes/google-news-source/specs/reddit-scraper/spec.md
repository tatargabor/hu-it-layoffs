## MODIFIED Requirements

### Requirement: Source display string
The `_source_str()` function in report.py SHALL format the source display string based on the `source` field:
- `source="reddit"` → `r/{subreddit}`
- `source="hup.hu"` → `hup.hu`
- `source="google-news"` → value of `news_source` field (e.g. "Portfolio.hu", "HVG", "Telex")

#### Scenario: Google News post in report
- **WHEN** a post has `source="google-news"` and `news_source="Portfolio.hu"`
- **THEN** the display string SHALL be `"Portfolio.hu"`

#### Scenario: Google News post with unknown source
- **WHEN** a post has `source="google-news"` and `news_source="unknown"`
- **THEN** the display string SHALL be `"unknown"`

#### Scenario: Reddit post unchanged
- **WHEN** a post has `source="reddit"` and `subreddit="programmingHungary"`
- **THEN** the display string SHALL be `"r/programmingHungary"` (unchanged behavior)
