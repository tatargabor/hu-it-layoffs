## 1. Dependencies

- [x] 1.1 Create `requirements.txt` with `googlenewsdecoder` and `trafilatura`
- [x] 1.2 Update `.github/workflows/pipeline.yml` to `pip install -r requirements.txt` before running pipeline

## 2. Scraper integration

- [x] 2.1 Add `_decode_gnews_url(gnews_url)` function in scraper.py — wraps `googlenewsdecoder`, returns real URL or None on failure, with 1.5s delay
- [x] 2.2 Add `_extract_article_content(url)` function in scraper.py — wraps `trafilatura.fetch_url` + `trafilatura.extract`, returns text or empty string, min 50 chars threshold
- [x] 2.3 Integrate into `run_google_news_scraper()`: after RSS parsing, for each new post call decode → extract → store in `selftext` field, replace `url` with real URL
- [x] 2.4 Add progress logging: "Fetching article content for N new Google News posts..."
- [x] 2.5 Re-enable Google News: change `ENABLED_SOURCES` from `["reddit"]` to `["reddit", "google-news"]`

## 3. Backfill script

- [x] 3.1 Create `scripts/backfill_gnews_content.py` — loads validated_posts.json, finds GN posts with empty selftext, decodes + extracts, saves back
- [x] 3.2 Run backfill on existing data, report success rate

## 4. Documentation update

- [x] 4.1 Update report.py methodology: mention Google News articles are now fetched with full content
- [x] 4.2 Update visualize.py methodology section similarly
- [x] 4.3 Re-generate report.md and report.html

## 5. Verify

- [x] 5.1 Test scraper with Google News enabled — verify new GN posts get selftext populated
- [x] 5.2 Verify LLM validation uses GN selftext (check that _build_prompt includes it)
