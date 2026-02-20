## Context

A scraper jelenleg 2 Reddit subredditről (r/programmingHungary, r/hungary) gyűjt adatot. A posztok egyszer kerülnek be a `raw_posts.json`-be és soha nem frissülnek. Ha egy poszt frissül (új kommentek, szerkesztett szöveg, változó score), a régi verzió marad.

## Goals / Non-Goals

**Goals:**
- Több Reddit subreddit keresése (r/layoffs, r/cscareerquestions)
- r/hungary query-k bővítése
- HUP.hu fórum scraping
- `source` mező hozzáadása és megjelenítése a reportokban
- Inkrementális frissítés: meglévő posztok updatelése (kommentek, score, szöveg)
- Zajos query szűkítése

**Non-Goals:**
- Social media scraping (LinkedIn, Facebook, Twitter)
- Bejelentkezést igénylő oldalak scraping-je
- Realtime / webhook-alapú figyelés

## Decisions

### 1. Inkrementális frissítés stratégia

**Döntés:** Merge-alapú megközelítés — a scraper betölti a meglévő `raw_posts.json`-t, és:
- Új posztok: hozzáadja
- Meglévő posztok: frissíti a `selftext`, `score`, `num_comments`, `top_comments` mezőket
- Post `id` marad a deduplikáció kulcsa

**Miért:** A Reddit API mindig a legfrissebb adatot adja, így a details fetch automatikusan frissíti a kommenteket. Csak be kell olvasni a régi adatot és merge-ölni.

**Alternatíva elvetése:** TTL-alapú (csak X napos posztokat frissít) — túl bonyolult, a Reddit API amúgy is a legfrissebb verziót adja.

### 2. HUP.hu scraping megközelítés

**Döntés:** `html.parser` stdlib modul + urllib — nincs külső függőség.

A HUP.hu struktúrája:
- Keresés: `https://hup.hu/search/node/<query>` — HTML eredménylista
- Topic oldal: HTML parse title, body, date, comments

**Miért:** stdlib-only policy, és a HUP.hu egyszerű HTML struktúrát használ ami html.parser-rel parsolható.

### 3. Scraper architektúra

**Döntés:** A `src/scraper.py` két fő funkciót kap:
- `run_reddit_scraper()` — a jelenlegi `run_scraper()` átnevezve
- `run_hup_scraper()` — új HUP.hu scraper
- `run_scraper()` — wrapper ami mindkettőt hívja és merge-öli az eredményt

A meglévő raw_posts.json merge logika:
```
1. Betölt meglévő raw_posts.json (ha van)
2. Futtat Reddit + HUP scraper
3. Merge: új posztok hozzáadása, meglévők frissítése
4. Ment raw_posts.json
```

### 4. Source mező

**Döntés:** `source` mező a post dict-ben:
- Reddit: `"reddit"` (a `subreddit` mező pontosítja melyik sub)
- HUP: `"hup.hu"`

A display-ben: `"r/{subreddit}"` Reddit esetén, `"hup.hu"` HUP esetén.

### 5. Új Reddit subreditek

**Döntés:** r/layoffs és r/cscareerquestions hozzáadása "Hungary OR Hungarian OR Budapest" query-vel. Ezek kis mennyiségű de potenciálisan értékes találatot adnak globális leépítések magyar vonatkozásáról.

## Risks / Trade-offs

- **HUP.hu HTML struktúra változhat** → Graceful degradation: ha a parse fail-el, log warning és skip. A HUP modul izolált, nem blokkolja a Reddit scraping-et.
- **Több subreddit = több 429 rate limit** → A REQUEST_DELAY (2s) elegendő kell legyen, de ha nem, exponential backoff bevezetése szükséges.
- **Inkrementális merge elveszítheti a törölt posztokat** → Nem probléma: ha egy poszt törlődik Reddit-ről, a régi verzió megmarad (ami inkább kívánatos viselkedés).
- **HUP.hu poszt id-k** → A HUP topic URL path-jéből származtatjuk (pl. `hup-12345`), prefix-szel elkerülve a Reddit id ütközést.
