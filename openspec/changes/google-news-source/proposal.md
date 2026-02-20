## Why

A projekt jelenleg Reddit-ről és HUP.hu-ról gyűjt adatot, de a magyar hírportálok (Portfolio, HVG, Telex, Index, 24.hu, stb.) leépítési híreit nem látja. A Google News RSS keresés egyetlen meta-forrásként aggregálja ezeket — nem kell portálonként scrapelni. A hírek hivatalos, megerősített adatokat adnak (pontos számok, cégnevek), amelyek kiegészítik a Reddit személyes beszámolóit. Az AI/mesterséges intelligencia munkahely-hatásairól szóló hírek is begyűjthetők ugyanezzel a mechanizmussal.

## What Changes

- Google News RSS scraper hozzáadása (`run_google_news_scraper()`) a meglévő scraper architektúrába
- Magyar nyelvű query-k: "leépítés IT", "elbocsátás programozó", "mesterséges intelligencia munkahely", "AI leépítés", cégspecifikus keresések
- Angol query-k magyar kontextussal: "tech layoff Budapest", "AI jobs Hungary"
- RSS XML parse stdlib `xml.etree.ElementTree`-vel
- `source="google-news"` mező, `news_source` almező a forrás portál nevével (pl. "Portfolio.hu")
- Forrás megjelenítése a report táblázatokban és dashboard-on

## Capabilities

### New Capabilities
- `google-news-scraper`: Google News RSS keresés — query-k futtatása, XML parse, poszt struktúra normalizálás a meglévő pipeline formátumra

### Modified Capabilities
- `reddit-scraper`: A `_source_str()` display logika bővítése google-news forrás kezelésével a reportban és dashboard-on

## Impact

- `src/scraper.py` — új `run_google_news_scraper()` + `GNEWS_QUERIES` config + `run_scraper()` bővítés
- `src/report.py` — `_source_str()` bővítés google-news forrás display-hez
- `src/visualize.py` — forrás oszlop kezelés google-news-hez
- Futási idő minimálisan nő (3-5 extra HTTP kérés, RSS parse gyors)
- Nincs új külső dependency (stdlib xml.etree.ElementTree)
