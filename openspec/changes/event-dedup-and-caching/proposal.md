## Why

A pipeline minden futáskor újra scrape-eli, elemzi és triage-olja az összes posztot — beleértve a 654 db 60 napnál régebbit (84%). Ez felesleges API hívás, idő és költség. Ezen felül a Google News egy eseményről 5-10 hírportál cikkét gyűjti be (pl. Audi Győr leépítés = 11 poszt), ami eltorzítja a statisztikákat: a szektormegoszlás, cégek száma és trend mind duplikált adatokra épül.

## What Changes

- **Persisted data layer (`persisted_data/`)**: >60 napos, validált posztok "fagyasztása" — a pipeline nem nyúl hozzájuk, csak a report merge-öli be
- **Scrape skip**: régi posztok (>60 nap) `fetch_post_details`-ét és triage/validálását skipeljük
- **Esemény deduplikáció (hibrid)**: az LLM validator visszaad egy `event_label` mezőt (pl. "Audi Győr 2026 Q1 leépítés"), a report/vizualizáció event_label-re csoportosít, így egy esemény = 1 sor a statban
- **Reddit `edited` mező gyűjtése**: a scraper lementi az `edited` timestampet a Reddit API-ból

## Capabilities

### New Capabilities
- `post-caching`: Validált posztok fagyasztása persisted_data/ könyvtárba, régi posztok skip-elése a pipeline-ban
- `event-dedup`: Hibrid esemény deduplikáció — LLM event_label + report-szintű csoportosítás

### Modified Capabilities

## Impact

- `src/scraper.py` — `edited` mező gyűjtése, régi poszt skip lehetőség
- `src/llm_validator.py` — `event_label` mező a SYSTEM_PROMPT-ban, `validate_posts()` skip régi fagyasztott posztok
- `src/report.py` — event_label csoportosítás a statisztikákban
- `src/visualize.py` — event_label csoportosítás a chartokban
- `src/run.py` — persisted_data merge logika, freeze lépés
- Új könyvtár: `persisted_data/`
