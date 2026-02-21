## 1. Source configuration in scraper

- [x] 1.1 Add `ENABLED_SOURCES` list to scraper.py config section (default: `["reddit"]`), with valid values: `reddit`, `google-news`, `hup`
- [x] 1.2 Guard `run_hup_scraper()` call in `run_scraper()` (line 538) — skip if `hup` not in `ENABLED_SOURCES`, log skip message
- [x] 1.3 Guard `run_google_news_scraper()` call in `run_scraper()` (line 541) — skip if `google-news` not in `ENABLED_SOURCES`, log skip message
- [x] 1.4 Log enabled/skipped sources at the start of `run_scraper()` (e.g. "Sources: reddit (enabled), google-news (skipped), hup (skipped)")
- [x] 1.5 Update `run_scraper()` docstring and module docstring (line 1-3) to reflect configurable sources

## 2. Documentation — report.py methodology

- [x] 2.1 Update header line (line 143): change `Forrás: Reddit, Google News, HUP.hu` → `Forrás: Reddit publikus adatok`
- [x] 2.2 Update methodology section (lines 320-356): remove Google News and HUP.hu as active sources, mention Reddit as sole active source, note historical GN data preserved
- [x] 2.3 Remove Google News limitation line (line 356) about magyar nyelvű vs vonatkozású

## 3. Documentation — visualize.py (HTML dashboard)

- [x] 3.1 Update dashboard subtitle (line 370): change `Reddit, Google News, HUP.hu publikus adatok` → `Reddit publikus adatok`
- [x] 3.2 Update methodology `<details>` section (lines 507-532): remove Google News and HUP.hu references, note Reddit as sole active source, mention historical data
- [x] 3.3 Update footer source line (line 540): keep dynamic source counts but update text context

## 4. Verify and test

- [x] 4.1 Run pipeline locally with `ENABLED_SOURCES = ["reddit"]` — verify no HUP/GN HTTP calls, only Reddit scrapes
- [x] 4.2 Verify existing Google News posts survive in validated_posts.json (historical data preserved)
- [x] 4.3 Check generated report.md and report.html methodology sections read correctly
