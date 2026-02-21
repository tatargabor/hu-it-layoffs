## Context

A magyar IT szektor leépítési trendjeit akarjuk dokumentálni Reddit publikus adatokból. Az explore fázisban már validáltuk, hogy az `old.reddit.com` JSON endpoint auth nélkül működik. Van 23 releváns poszt egy előzetes `data.json`-ban. Most ezt kell kibővíteni, mélyíteni, és strukturált riportba önteni.

## Goals / Non-Goals

**Goals:**
- Teljes Reddit scrape `r/programmingHungary` és `r/hungary` subredditekről IT leépítés témában
- Posztok tartalmának (selftext + top kommentek) letöltése a részletes elemzéshez
- Érintett cégek és becslések kinyerése a posztokból
- Nyitott pozíciók / hiring freeze jelek azonosítása
- Markdown riport generálás publikálható minőségben
- Minden Python stdlib — nulla külső dependency

**Non-Goals:**
- Valós idejű monitoring vagy ismétlődő scrape
- LinkedIn, Facebook, vagy más platform scrape
- Sentiment analysis vagy ML klasszifikáció
- Webszerver vagy dashboard

## Decisions

### 1. old.reddit.com JSON API auth nélkül
**Döntés:** `old.reddit.com/r/{sub}/search.json` endpointot használjuk, nem az OAuth API-t.
**Alternatíva:** Reddit OAuth API (script app) — de a reCAPTCHA nem működött a user Chrome-jában, és az auth nélküli endpoint tökéletesen elegendő publikus kereséshez.
**Kockázat:** Rate limiting (429). Megoldás: 1.5 sec sleep requestek között.

### 2. Python stdlib only
**Döntés:** Csak `urllib`, `json`, `datetime`, `re` — semmi pip install.
**Alternatíva:** `requests` + `praw` (Reddit Python lib). Felesleges dependency egy egyszeri scrape-hez.

### 3. Két fázisú scrape: keresés → poszt részletek
**Döntés:** Először search API-val gyűjtünk poszt ID-kat, utána egyenként letöltjük a poszt selftext-jét és top kommentjeit a részletes elemzéshez.
**Rationale:** A search API nem adja vissza a teljes selftext-et és a kommenteket, de a becslésekhez és cég-azonosításhoz ezek kellenek.

### 4. Heurisztikus becslés ahol nincs szám
**Döntés:** Ha a poszt nem tartalmaz konkrét létszámot, a kontextusból becsülünk (pl. "nagy leépítés" multinál = 50-200, startup = 10-30). Minden becslés `~` prefixszel jelölt a riportban.
**Alternatíva:** Csak ahol van konkrét szám. De ez a posztok ~70%-át kihagyná.

### 5. File struktúra

```
src/
├── scraper.py          # Reddit JSON API scrape
├── analyzer.py         # Poszt elemzés, cég + szám kinyerés
├── report.py           # Markdown riport generálás
├── visualize.py        # HTML dashboard generálás (Chart.js CDN)
└── run.py              # Fő belépési pont — mindent futtat
data/
├── raw_posts.json      # Nyers scrape eredmény
├── analyzed_posts.json # Elemzett, dúsított adatok
├── report.md           # Végső riport (markdown)
└── report.html         # Interaktív dashboard (Chart.js)
```

## Risks / Trade-offs

- **[Rate limiting]** → 2.0s sleep requestek között, max 100 poszt/query (Reddit limit). 1.5s-sel 429-eket kaptunk.
- **[Adathiány]** → A Reddit search max ~250 eredményt ad vissza queryenként, régebbi posztok hiányozhatnak → több különböző query-vel fedünk le többet
- **[Becslés pontatlansága]** → Minden becslést jelölünk, range-et adunk (pl. ~50-100), nem pontos számot
- **[Encoding]** → Magyar ékezetes karakterek URL encoding-ja trükkös az `old.reddit.com`-on → `urllib.parse.quote()` megoldja
