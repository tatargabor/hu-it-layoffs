## 1. Project Setup

- [x] 1.1 Create `src/` and `data/` directory structure
- [x] 1.2 Create `src/run.py` entry point that orchestrates scraper → analyzer → report

## 2. Reddit Scraper (`src/scraper.py`)

- [x] 2.1 Implement multi-keyword search across `r/programmingHungary` and `r/hungary` using `old.reddit.com` JSON API
- [x] 2.2 Add pagination support (follow `after` token, max 5 pages per query)
- [x] 2.3 Implement post detail fetching (selftext + top 20 comments per post)
- [x] 2.4 Add rate limiting (1.5s between requests, 10s retry on 429)
- [x] 2.5 Deduplicate posts by ID across all queries
- [x] 2.6 Save results to `data/raw_posts.json`

## 3. Post Analyzer (`src/analyzer.py`)

- [x] 3.1 Implement company extraction from title, selftext, and comments (known-companies list + freeform detection)
- [x] 3.2 Implement headcount estimation (explicit number extraction + heuristic ranges)
- [x] 3.3 Implement relevance scoring (0-3 scale: direct layoff, strong signal, indirect, not relevant)
- [x] 3.4 Implement AI attribution detection (AI mentioned as cause in post or comments)
- [x] 3.5 Implement hiring freeze signal detection
- [x] 3.6 Categorize posts (layoff / freeze / anxiety / other)
- [x] 3.7 Save results to `data/analyzed_posts.json`

## 4. Report Generator (`src/report.py`)

- [x] 4.1 Generate summary section (key numbers, date range)
- [x] 4.2 Generate quarterly timeline (2023 Q1 – 2026 Q1, post count + companies + headcount per quarter)
- [x] 4.3 Generate company summary table (company, dates, headcount, source links, AI-attributed)
- [x] 4.4 Generate aggregate statistics (total posts, companies, headcount range, AI mentions, freeze signals)
- [x] 4.5 Generate trend analysis section (frequency trend, sector breakdown, AI attribution trend)
- [x] 4.6 Generate hiring signals section (hiring freeze posts with quotes)
- [x] 4.7 Generate data sources section (all posts as markdown links, sorted by date)
- [x] 4.8 Write final report to `data/report.md`

## 5. Run & Verify

- [x] 5.1 Run full pipeline (`python src/run.py`) and verify output
- [x] 5.2 Manually review `data/report.md` for completeness and accuracy
