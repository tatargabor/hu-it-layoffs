## Why

A magyar IT szektorban 2023 óta fokozódó leépítési hullám zajlik, amit a globális tech winter, majd az AI-vezérelt piaci átárazás hajt. Nincs egyetlen helyen összegyűjtött, strukturált kimutatás erről — csak szétszórt Reddit posztok és hírek. Ezt a riportot azért készítjük, hogy konkrét adatokkal dokumentáljuk a trendet.

## What Changes

- Reddit scraper amely `r/programmingHungary` és `r/hungary` subredditekből gyűjti az IT leépítés/elbocsájtás posztokat (publikus JSON API, auth nélkül)
- Többszintű kulcsszó-keresés magyar és angol kifejezésekre (leépítés, elbocsájtás, layoff, kirúgás, quiet firing, stb.)
- Poszt deduplikáció és relevancia-szűrés
- Érintett emberek számának becslése ahol nincs konkrét szám (poszt kontextus alapján)
- Nyitott IT pozíciók / felvételi freeze detektálás
- Markdown riport generálás: timeline, érintett cégek, becslések, trendek

## Capabilities

### New Capabilities
- `reddit-scraper`: Reddit publikus JSON API-ból posztok gyűjtése kulcsszavak alapján, rate limiting, pagination, több subreddit támogatás
- `post-analyzer`: Posztok tartalmának elemzése — érintett cég azonosítása, létszám becslés, AI-attributáció, relevancia scoring
- `report-generator`: Strukturált markdown riport generálás a feldolgozott adatokból — timeline, cég-összesítő, trend-analízis, nyitott pozíciók
- `html-visualizer`: Interaktív HTML dashboard Chart.js-szel (CDN) — negyedéves timeline, cég bar chart, szektor/kategória doughnut, AI trend, poszt táblázat

### Modified Capabilities

(nincs — új projekt)

## Impact

- Új Python scriptek a projekt gyökerében (`src/` könyvtár)
- Külső függőség: csak Python stdlib (urllib, json) — nincs pip install. Chart.js CDN-ről töltődik a HTML-ben.
- Output: `data/` könyvtár JSON adatokkal + `report.md` markdown riport + `report.html` interaktív dashboard
