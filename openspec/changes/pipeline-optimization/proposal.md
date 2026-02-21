## Why

A napi pipeline CI-ben ~43 percig fut. A legtöbb idő feleslegesen megy el: a scraper minden futásnál MINDEN query-t lefuttat és MINDEN posztot újra leszedi, a batch triage minden nem-frozen posztot újra szűr, és a Reddit fetch_post_details régi posztokra is hívódik. A frozen posts mechanizmus csak 60 napos posztokra vonatkozik, közben a 2-59 napos posztok minden futásnál újra feldolgozódnak. A felhasználó kifejezetten kérte: "a régebbi reddit postokat le sem kellene újra fetchelni, az LLM validate meg ha nem forceoljuk nem kellene csak az újakra fusson".

## What Changes

- **Scraper early termination**: Ha egy Reddit search query-ben elérjük az ismert posztokat (már raw_posts.json-ban vannak), ne lapozzunk tovább — nincs új poszt hátrább
- **Google News / HUP skip**: Ha egy cikk ID-je már megvan a raw_posts.json-ban, ne szedd le újra (nincs score/comment update ezeknél)
- **Reddit fetch_post_details skip**: Ne hívj fetch_post_details-t olyan posztra ami már rendelkezik top_comments-szel ÉS nem friss (>7 nap) — kommentek nem változnak lényegesen
- **Batch triage skip**: Már `llm_validated=True` posztokat ne futtasd újra a batch triage-on, csak az újonnan scrapelt posztokat
- **LLM validate skip (meglévő, javítás)**: A jelenlegi skip logika működik (`llm_validated` + `llm_sector` + `llm_hungarian_relevance` + `llm_event_label`), de a batch triage feleslegesen fut rájuk
- **HUP.hu scraper opcionális skip**: A HUP.hu ~44 request-et küld 0 hasznos eredményért — legyen kikapcsolható env var-ral
- **REQUEST_DELAY csökkentés non-Reddit forrásokra**: Google News RSS és HUP.hu nem igényel 2s delay-t, 0.5s elég

## Capabilities

### New Capabilities
- `incremental-scraping`: Scraper felismeri a már meglévő posztokat és skipeli a felesleges fetch-eket, early termination a Reddit pagination-ben
- `incremental-llm`: Batch triage és LLM validáció csak az új/módosult posztokra fut, nem az összes nem-frozen posztra

### Modified Capabilities

## Impact

- `src/scraper.py` — early termination, skip logic, REQUEST_DELAY differenciálás
- `src/llm_validator.py` — batch_triage és validate_posts skip logika javítás
- `src/run.py` — existing post ID-k átadása a scrapernek, validated post ID-k átadása az LLM-nek
- `.github/workflows/pipeline.yml` — opcionális HUP skip env var
- Várható eredmény: ~43 perc → ~15-20 perc (napi inkrementális futás), első futás változatlan
