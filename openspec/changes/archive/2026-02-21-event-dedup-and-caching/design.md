## Context

A pipeline 777 posztot kezel, ebből 654 (84%) 60 napnál régebbi. Minden futáskor az összes posztot újra scrape-eli (Reddit paginálás + kommentek letöltése), triage-olja és potenciálisan újra-validálja. A Google News egy leépítési eseményről 5-10 különböző portál cikkét gyűjti be (pl. Audi Győr jan 2026 = 11 poszt). A statisztikák (szektormegoszlás, cégek száma, trend) ezért torzulnak.

Jelenlegi adatfolyam:
```
Scrape ALL → Analyze ALL → Triage ALL → Validate (skip llm_validated) → Report
```

A validate lépés már skipeli az `llm_validated=True` posztokat, de a scrape, analyze és triage minden futáskor az egész adatbázisra fut.

## Goals / Non-Goals

**Goals:**
- `persisted_data/` könyvtár: régi, validált posztok fagyasztása, pipeline nem nyúl hozzájuk
- Scrape/triage/validate skip régi (>60 nap) fagyasztott posztokra
- LLM `event_label` mező: normalizált esemény azonosító (pl. "Audi Győr 2026 Q1 leépítés")
- Report/vizualizáció event_label csoportosítás: egy esemény = 1 sor a statban, de minden poszt megmarad a részletes táblázatban
- Reddit `edited` mező gyűjtése a scraper-ben

**Non-Goals:**
- Régi posztok törlése — megmaradnak, csak fagyasztva
- Google News query-k szűkítése — a szűrés LLM + dedup szinten történik
- HUP.hu változtatás — jelenleg nincs HUP poszt az adatban

## Decisions

### 1. Persisted data struktúra

```
persisted_data/
└── frozen_posts.json    ← >60 napos, validált posztok
```

Egyetlen JSON fájl, mint a jelenlegi `data/validated_posts.json`. Nem kell per-poszt fájl — a 654 poszt egyetlen fájlban jól kezelhető (~2MB).

**Freeze feltétel:** `llm_validated == True` ÉS `date < (now - 60 nap)` ÉS `llm_hungarian_relevance` mező megvan.

**Miért nem per-poszt fájl:** Egyetlen JSON egyszerűbb, a git diff is átláthatóbb. 777 poszt nem indokol fájlrendszer-szintű shardolást.

### 2. Pipeline flow módosítás

```
Új flow:
1. Load frozen_posts.json (régi, kész posztok)
2. Scrape ONLY fresh (Reddit: <60 nap cutoff, GNews: RSS amúgy is friss)
3. Analyze fresh
4. Triage fresh
5. Validate fresh (+ unfrozen ami nincs kész)
6. Merge: frozen + fresh = validated_posts.json
7. Freeze: validált + >60 nap → persisted_data/frozen_posts.json
8. Report (merged adatból)
```

A freeze lépés a pipeline végén fut — ami most validálódott és régi, az fagyasztódik a következő futásra.

### 3. Reddit scrape cutoff

A `run_scraper()` megkapja a cutoff dátumot. Az `_merge_posts()`-nál a régi, már fagyasztott posztokat nem kell újra fetch-elni.

Konkrétan: ha egy poszt `id` már benne van a `frozen_posts.json`-ban, ne hívjunk `fetch_post_details()`-t rá.

A Reddit API nem ad `last_modified` headert a search-re, de az `edited` mező (false vagy Unix timestamp) mutatja ha a poszt módosult. Ezt lementjük, de cutoff felett akkor sem frissítjük.

### 4. Event deduplikáció — hibrid megközelítés

**LLM szint:** A SYSTEM_PROMPT kap egy `event_label` mezőt:
```json
{
  "event_label": "Audi Győr 2026 Q1 leépítés"
}
```

Az LLM normalizálja az eseményt: `[Cég] [Helyszín opcionális] [Év] [Negyedév] [típus]`. Ha nem leépítés hanem freeze/anxiety, a label null.

**Report szint:** A `report.py` és `visualize.py` a statisztikáknál (szektormegoszlás, cégek száma, timeline) az `event_label`-re group-by-ol:
- Egy event = 1 egység a statban
- A poszt listákban (részletes táblázat, források) minden poszt megmarad
- A "legtöbb reakció" top-5 poszt-szinten marad (nem event)

**Miért nem fuzzy matching:** Az LLM amúgy is látja a cikk tartalmát — a normalizált event_label megbízhatóbb mint cég+dátum heurisztika. Plusz a cég neve nem mindig konzisztens (OTP vs OTP Bank).

### 5. Freeze és event_label együttműködés

A freeze a pipeline végén fut, az event_label a validate lépésben töltődik ki. Tehát a frozen posztoknak már megvan az event_label-jük — a report merge után azonnal csoportosítható.

Újra-validálási trigger: ha `llm_validated=True` de `llm_event_label` hiányzik → újra-validálni (mint a hungarian_relevance-nél).

## Risks / Trade-offs

- **[Event label inkonzisztencia]** Különböző futásokban az LLM más labelt adhat ugyanarra az eseményre. → Mitigation: a frozen posztok labelje nem változik (nem validáljuk újra). Csak friss posztok kapnak labelt.
- **[Frozen poszt frissítés]** Ha egy régi poszt score/komment számát kellene frissíteni, a freeze megakadályozza. → Mitigation: >60 napos Reddit poszt score-ja már nem változik érdemben.
- **[Első freeze futás költsége]** Az event_label mező kitöltéséhez az összes meglévő posztot újra kell validálni. → Mitigation: egyszer kell, utána inkrementális. Az Anthropic Haiku ~$0.18/futás.
- **[persisted_data git méret]** A frozen_posts.json ~2MB a git-ben. → Mitigation: nem nő gyorsan (60 nap felettiek, ~10-20 poszt/hónap). Elfogadható.
