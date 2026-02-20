## 1. Reddit scraper bővítés (`src/scraper.py`)

- [x] 1.1 Add `source: "reddit"` field to every post dict in `search_subreddit()`
- [x] 1.2 Expand r/hungary queries: add `álláskereső OR álláspiac`, `hiring freeze`, `Ericsson OR Continental OR OTP OR NNG OR Lensa OR Microsoft leépítés`
- [x] 1.3 Add r/layoffs subreddit with query `Hungary OR Hungarian OR Budapest`
- [x] 1.4 Add r/cscareerquestions subreddit with query `Hungary OR Hungarian OR Budapest`
- [x] 1.5 Narrow noisy query: `munkanélküli OR nincs munka` → `munkanélküli IT OR nincs munka programozó OR nincs munka fejlesztő`

## 2. Inkrementális frissítés (`src/scraper.py`)

- [x] 2.1 In `run_scraper()`, load existing `raw_posts.json` if it exists
- [x] 2.2 Merge logic: new posts added, existing posts updated (selftext, score, num_comments, top_comments)
- [x] 2.3 Keep post `id` as deduplication key across all sources

## 3. HUP.hu scraper (`src/scraper.py`)

- [x] 3.1 Add `run_hup_scraper()` function using urllib + html.parser
- [x] 3.2 Implement HUP.hu search page parsing (`hup.hu/search/node/<query>`)
- [x] 3.3 Implement HUP topic page parsing (title, date, body, comments)
- [x] 3.4 Use `hup-<id>` prefix for post IDs to avoid Reddit ID collision
- [x] 3.5 Set `source: "hup.hu"` and `subreddit: "hup.hu"` on HUP posts
- [x] 3.6 Add rate limiting (2s delay between requests)
- [x] 3.7 Graceful degradation: if HUP.hu is unreachable, log warning and continue

## 4. Scraper orchestration (`src/scraper.py`)

- [x] 4.1 Rename current `run_scraper()` to `run_reddit_scraper()`
- [x] 4.2 New `run_scraper()` wrapper that calls both Reddit and HUP scrapers
- [x] 4.3 Merge results from all sources, pass to `save_raw_posts()`

## 5. Source tracking in pipeline (`src/analyzer.py`, `src/llm_validator.py`)

- [x] 5.1 Pass through `source` field in analyzer output
- [x] 5.2 Pass through `source` field in LLM validator output

## 6. Source in markdown report (`src/report.py`)

- [x] 6.1 Add source column to company table
- [x] 6.2 Add source column to detailed table
- [x] 6.3 Add source breakdown summary (posts per source)

## 7. Source in HTML dashboard (`src/visualize.py`)

- [x] 7.1 Add source column to top posts table
- [x] 7.2 Add source column to detailed (collapsible) table
- [x] 7.3 Add source distribution chart or summary stat
- [x] 7.4 Display source as "r/{subreddit}" for Reddit, "hup.hu" for HUP

## 8. Verify

- [x] 8.1 Run pipeline — verify new subreddits produce results
- [x] 8.2 Verify HUP.hu scraping works (or gracefully skips)
- [x] 8.3 Verify incremental update: run twice, check posts are updated not duplicated
- [x] 8.4 Verify source column appears in HTML and markdown tables
- [x] 8.5 Verify source breakdown statistics are correct
