## 1. Google News scraper implementáció

- [x] 1.1 `GNEWS_QUERIES` lista definiálása `src/scraper.py`-ban (magyar IT leépítés, AI munkahely, cégspecifikus, angol query-k)
- [x] 1.2 `run_google_news_scraper()` függvény: query-k futtatása, RSS XML fetch `_fetch_html()`-lel, `xml.etree.ElementTree` parse
- [x] 1.3 pubDate parse `email.utils.parsedate_to_datetime`-mal, fallback mai dátumra
- [x] 1.4 Post normalizálás: `gnews-` prefix ID (SHA256 title+date), standard post dict struktúra, `news_source` mező
- [x] 1.5 Deduplikáció query-ken belül (id kulcs alapján)

## 2. Pipeline integráció

- [x] 2.1 `run_scraper()` bővítése: `run_google_news_scraper()` hívás és merge a Reddit + HUP eredmények mellé
- [x] 2.2 `_source_str()` bővítése `src/report.py`-ban: `source="google-news"` → `news_source` mező megjelenítése
- [x] 2.3 `_source_str()` / forrás display bővítése `src/visualize.py`-ban google-news forrás kezeléshez

## 3. Tesztelés

- [x] 3.1 Futtatás: `run_google_news_scraper()` önálló teszt — query-k futnak, RSS parse működik, posztok visszajönnek
- [ ] 3.2 Teljes pipeline teszt: `python -m src.run` — google-news posztok megjelennek a reportban helyes forrás display-jel
