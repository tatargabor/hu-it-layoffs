## 1. Post caching — persisted_data infrastruktúra

- [x] 1.1 `persisted_data/` könyvtár létrehozása, `.gitignore`-ba `persisted_data/*.json` hozzáadása (ne commitoljuk a nagy JSON-t, csak a könyvtárat)
- [x] 1.2 `src/run.py` — `_load_frozen_posts()` és `_save_frozen_posts()` helper függvények: `persisted_data/frozen_posts.json` load/save
- [x] 1.3 `src/run.py` — freeze lépés a pipeline végén: validált + >60 napos + `llm_hungarian_relevance` meglévő posztok → `frozen_posts.json`
- [x] 1.4 `src/run.py` — pipeline elején frozen posztok betöltése, merge a végén: frozen + fresh → `validated_posts.json`

## 2. Scrape/triage/validate skip frozen posztokra

- [x] 2.1 `src/scraper.py` — `fetch_post_details()` skip ha poszt ID a frozen setben (frozen_ids paraméter a `run_scraper()`-nek)
- [x] 2.2 `src/scraper.py` — Reddit `edited` mező gyűjtése a `search_subreddit()` és `fetch_post_details()`-ben
- [x] 2.3 `src/llm_validator.py` — `batch_triage()` skip frozen posztok (frozen_ids paraméter)
- [x] 2.4 `src/llm_validator.py` — `validate_posts()` skip frozen posztok (frozen_ids paraméter)

## 3. Event deduplikáció — LLM event_label

- [x] 3.1 `src/llm_validator.py` — SYSTEM_PROMPT JSON séma bővítése `event_label` mezővel + mező leírás és példák
- [x] 3.2 `src/llm_validator.py` — `validate_posts()` `llm_event_label` mező mentése a poszt dict-be
- [x] 3.3 `src/llm_validator.py` — re-validálási trigger: `llm_event_label` nélküli `llm_validated=True` posztok újra-validálása

## 4. Report/vizualizáció event-szintű csoportosítás

- [x] 4.1 `src/report.py` — event-szintű helper: `_unique_events(posts)` → event_label-re group-by, egy event = 1 egység
- [x] 4.2 `src/report.py` — szektormegoszlás, cégek száma, timeline: event-szintű számolás (nem poszt-szintű)
- [x] 4.3 `src/visualize.py` — company chart, sector chart, timeline chart: event-szintű számolás
- [x] 4.4 `src/report.py` + `src/visualize.py` — részletes táblázat és poszt listák: poszt-szintű marad (nem csoportosít)

## 5. Validálás

- [x] 5.1 Pipeline futtatás — ellenőrzés: `persisted_data/frozen_posts.json` létrejön, frozen posztok skipelődnek
- [x] 5.2 Ellenőrzés: `llm_event_label` mező megjelenik a validated_posts.json-ban
- [x] 5.3 Ellenőrzés: Audi 11 poszt → 1 event a statban, de 11 sor a részletes táblázatban
