## Why

A projekt jelenleg csak 2 subredditről (r/programmingHungary, r/hungary) gyűjt adatot, limitált query-készlettel. Emiatt releváns leépítési hírek kimaradhatnak. Több Reddit subreddit és magyar IT fórum (HUP.hu) bevonásával teljesebb képet kapunk. A táblázatokban és chartokban meg kell jelennie a forrásnak is, hogy átlátható legyen honnan származik az adat.

## What Changes

- Scraper bővítése új Reddit subredditekkel: r/layoffs, r/cscareerquestions (Hungary szűréssel)
- r/hungary query-k bővítése (álláspiac, hiring freeze, cégnevek)
- HUP.hu fórum scraper hozzáadása (HTML scraping, stdlib urllib + html.parser)
- Zajos query (`munkanélküli OR nincs munka`) szűkítése relevancia javítására
- `source` mező hozzáadása minden poszthoz (pl. "reddit/programmingHungary", "hup.hu")
- Forrás oszlop megjelenítése a HTML dashboard és markdown report táblázataiban
- Forrás szerinti bontás a statisztikákban (doughnut chart vagy summary)

## Capabilities

### New Capabilities
- `hup-scraper`: HUP.hu fórum scraping — HTML parsing, relevans topicok keresése, poszt struktúra kinyerése
- `source-tracking`: Forrás mező hozzáadása a pipeline-hoz és megjelenítés a report/dashboard táblázataiban

### Modified Capabilities
- `reddit-scraper`: Új subredditek (r/layoffs, r/cscareerquestions), r/hungary bővített query-k, zajos query szűkítése

## Impact

- `src/scraper.py` — SUBREDDIT_QUERIES bővítés + HUP scraper funkciók
- `src/analyzer.py` — source mező kezelése
- `src/report.py` — forrás oszlop a táblázatokban, forrás szerinti statisztika
- `src/visualize.py` — forrás oszlop a HTML táblákban, forrás chart
- Futási idő nő (több query + HUP scraping), de CI-ben ez elfogadható
