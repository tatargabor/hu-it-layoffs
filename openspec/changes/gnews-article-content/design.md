## Context

Google News RSS only provides article titles — no body text. The spike test confirmed that `googlenewsdecoder` can resolve GN RSS URLs to real article URLs (15/15 success rate), and `trafilatura` can extract clean article text (1-4K chars) from Hungarian news portals (Blikk, VG.hu, Portfolio, Startlap, etc.) without headless browser.

Currently Google News is disabled (`ENABLED_SOURCES = ["reddit"]`). This change re-enables it with full article content.

## Goals / Non-Goals

**Goals:**
- Decode Google News RSS URLs to real article URLs using `googlenewsdecoder`
- Extract article body text using `trafilatura` and store in `selftext` field
- Re-enable Google News in `ENABLED_SOURCES`
- Provide a one-time backfill for existing 449 GN posts
- LLM validation can then analyze GN posts with full article context (not just title)

**Non-Goals:**
- Headless browser — not needed, `trafilatura` handles it
- Re-enabling HUP.hu — stays disabled (0 posts, dead source)
- Changing LLM validation logic — it already uses `selftext[:1500]`, so GN posts automatically benefit

## Decisions

### D1: Library choice for URL decoding
**Decision**: Use `googlenewsdecoder` (pip package, 0.1.7).
**Rationale**: Google News uses protobuf-encoded URLs that can't be base64-decoded directly. This lib handles the decoding reliably (15/15 in spike). Lightweight dependency.
**Alternative**: Headless browser to follow JS redirect — rejected, much heavier and slower.

### D2: Library choice for content extraction
**Decision**: Use `trafilatura` (pip package).
**Rationale**: Purpose-built for article extraction. Handles Hungarian portals well (tested: Blikk, VG.hu, Portfolio, Startlap, Femina, Magyar Jelen). No JS rendering needed.
**Alternative**: `newspaper3k` — older, less maintained. `beautifulsoup` manual parsing — too brittle across many portals.

### D3: Integration point
**Decision**: Add extraction step inside `run_google_news_scraper()`, after RSS parsing. Each new GN post gets URL decoded + article extracted inline. Store in existing `selftext` field.
**Rationale**: Keeps the data model unchanged. LLM validator already reads `selftext[:1500]` — no changes needed downstream.

### D4: Backfill approach
**Decision**: Standalone script `scripts/backfill_gnews_content.py` that loads `data/validated_posts.json`, finds GN posts with empty selftext, decodes URLs, extracts content, and saves back.
**Rationale**: One-time operation. Separate from pipeline so it can be run independently.

### D5: Rate limiting
**Decision**: 1.5s delay between `googlenewsdecoder` calls (it makes HTTP requests to Google). `trafilatura` fetch has its own built-in rate limiting.
**Rationale**: Avoid triggering Google rate limits. 449 posts × 1.5s ≈ 11 minutes for full backfill — acceptable.

## Risks / Trade-offs

- **[Some articles behind paywall]** → `trafilatura` extracts what's available (often the lead paragraph is enough). Posts with < 50 chars extracted text get `selftext` left empty.
- **[googlenewsdecoder depends on Google's internal format]** → If Google changes the URL format, the lib may break. Mitigation: graceful fallback — if decode fails, GN post keeps empty selftext (title-only validation as before).
- **[Increased scraper runtime]** → ~1.5s per GN article × ~50 new articles/run ≈ 75s extra. Acceptable for daily CI.
