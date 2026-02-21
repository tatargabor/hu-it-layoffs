## Why

A Google News RSS és HUP.hu források csak címalapú elemzést tesznek lehetővé (0 body, 0 comment), ami sekélyes validációt eredményez. A Google News ráadásul masszív duplikációt hoz (pl. OTP leépítés 8x, Audi 7x különböző portálokról), és a posztok ~80%-a nem IT szektor (autógyár, posta, retail). Ez megduplázza az LLM költséget (287 extra validáció) érdemi hozzáadott érték nélkül. A HUP.hu gyakorlatilag halott — 0 poszt az adatban. A Reddit ezzel szemben 98%-ban rendelkezik body text-tel és 82%-ban kommentekkel, ami mély, kontextuális elemzést tesz lehetővé.

## What Changes

- **Disable** Google News RSS scraper (kód marad, de nem fut — flag-gel kikapcsolva)
- **Disable** HUP.hu forum scraper (kód marad, de nem fut — flag-gel kikapcsolva)
- **Update** pipeline to run Reddit-only by default
- **Update** README.md methodology section — csak Reddit mint aktív forrás
- **Update** HTML dashboard — forrás-hivatkozások frissítése, csak Reddit látszódjon aktív forrásként
- **Update** report.py — methodology szöveg frissítése

## Capabilities

### New Capabilities
- `source-management`: Configuration for enabling/disabling data sources (Reddit, Google News, HUP) via flags, so disabled sources can be re-enabled later if needed

### Modified Capabilities
_(No existing specs to modify)_

## Impact

- `src/scraper.py`: Google News és HUP scraper függvények skip-elése ha disabled
- `src/run.py`: Pipeline csak Reddit scraper-t hívja alapértelmezetten
- `src/report.py`: Methodology szekció szöveg frissítése
- `src/visualize.py`: Dashboard forrás-leírás frissítése
- `README.md`: Methodology szekció frissítése
- `.github/workflows/pipeline.yml`: Nincs változás (már csak Anthropic-ot használ)
- `data/validated_posts.json`: Meglévő Google News posztok maradnak (historikus adat), de új nem jön
