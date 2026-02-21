## Why

A Google News RSS csak címeket ad — a 449 GN posztnak 0 body és 0 comment van. Emiatt az LLM validáció kizárólag címalapú, ami nem elég pontos (pl. Audi gyári leépítést nem tudja megkülönböztetni Audi IT leépítéstől). Spike teszt bizonyította: `googlenewsdecoder` + `trafilatura` kombóval headless browser nélkül 15/15 cikkből sikerült szöveget kinyerni (1-4K karakter). Ez lehetővé teszi a Google News forrás újraengedélyezését teljes tartalom-alapú validációval.

## What Changes

- **Add** Google News URL decoding (`googlenewsdecoder` lib) — a GN RSS URL-ekből kinyeri a valódi cikk URL-t
- **Add** Article content extraction (`trafilatura` lib) — a valódi URL-ből kinyeri a cikk szöveget
- **Integrate** into scraper pipeline: GN posztok kapnak `selftext` mezőt a cikk szöveggel
- **Add** backfill script: meglévő 449 GN poszt utólagos feltöltése cikk szöveggel
- **Re-enable** Google News source in `ENABLED_SOURCES` default config
- **Update** dependencies: `googlenewsdecoder`, `trafilatura` hozzáadása

## Capabilities

### New Capabilities
- `article-extraction`: Google News cikk URL feloldása és tartalom kinyerése a scraper pipeline-ban

### Modified Capabilities
_(No existing specs)_

## Impact

- `src/scraper.py`: `run_google_news_scraper()` bővítése URL decode + content extraction lépéssel
- `src/scraper.py`: `ENABLED_SOURCES` visszaállítása `["reddit", "google-news"]`-re
- `requirements.txt` vagy inline dependency: `googlenewsdecoder`, `trafilatura`
- `data/validated_posts.json`: meglévő GN posztok `selftext` mezője feltöltődik
- LLM validáció minőség javul: cikk szöveg alapú elemzés a cím helyett
