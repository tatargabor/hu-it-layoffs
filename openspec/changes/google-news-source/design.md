## Context

A scraper (`src/scraper.py`) jelenleg két forrást kezel: Reddit (`run_reddit_scraper()`) és HUP.hu (`run_hup_scraper()`). Mindkettő dict-et ad vissza `{id: post}` formátumban, amit a `run_scraper()` merge-öl. A Google News RSS ugyanebbe a mintába illeszkedik.

A Google News RSS endpoint: `https://news.google.com/rss/search?q=QUERY&hl=hu&gl=HU&ceid=HU:hu`
- Visszaad XML-t standard RSS 2.0 formátumban
- Minden `<item>` tartalmaz: `<title>`, `<link>`, `<pubDate>`, `<source>` (portál neve)
- A link Google redirect URL (`news.google.com/rss/articles/...`), nem a tényleges cikk URL
- Nincs cikk body/selftext — csak cím elérhető

## Goals / Non-Goals

**Goals:**
- Google News RSS keresés integrálása a meglévő scraper pipeline-ba
- Magyar IT leépítési és AI munkaerőpiaci hírek begyűjtése
- Forrás portál neve megőrzése (Portfolio.hu, HVG, Telex, stb.)
- A post dict formátum kompatibilis marad a meglévő pipeline-nal (analyzer, LLM validator, report)

**Non-Goals:**
- Google redirect URL-ek feloldása (a tényleges cikk URL kinyerése) — a Google link elegendő
- Cikk body scraping az eredeti portálról — az LLM validáció cím alapján is működik
- Google News API (fizetős) használata — RSS ingyenes és elégséges
- Duplikáció-kezelés Reddit és Google News között (ugyanaz az esemény, más forrás) — ez későbbi fejlesztés

## Decisions

### 1. RSS parse módszer

**Döntés:** `xml.etree.ElementTree` stdlib modul az RSS XML parse-hoz.

**Miért:** Stdlib-only policy (mint a HUP.hu scraper), és az RSS 2.0 egyszerű XML struktúra:
```xml
<rss><channel>
  <item>
    <title>Leépítés az Audinál</title>
    <link>https://news.google.com/rss/articles/...</link>
    <pubDate>Wed, 14 Jan 2026 08:00:00 GMT</pubDate>
    <source url="https://portfolio.hu">Portfolio.hu</source>
  </item>
</channel></rss>
```

### 2. Query készlet

**Döntés:** Két kategória query:

Magyar nyelvű:
- `leépítés IT`
- `elbocsátás programozó`
- `leépítés informatikus`
- `mesterséges intelligencia munkahely`
- `AI leépítés`
- `hiring freeze Magyarország`

Angol nyelvű magyar kontextussal:
- `tech layoff Hungary`
- `AI jobs Budapest`

Cégspecifikus:
- `Ericsson leépítés`, `Audi leépítés`, `Continental leépítés`, `OTP leépítés`

**Miért:** A Google News kereső jól szűr nyelvre (`hl=hu&gl=HU`), de angol query-k is adhatnak magyar vonatkozású eredményt. A cégspecifikus query-k biztosítják, hogy ismert nagy cégek leépítései ne maradjanak ki.

### 3. Post ID séma

**Döntés:** `gnews-<hash>` formátum, ahol a hash a cím + dátum SHA256-ának első 10 karaktere.

**Miért:** A Google News RSS-ben nincs stabil egyedi azonosító. A cím + dátum kombináció kellően egyedi és determinisztikus (ugyanaz a cikk mindig ugyanazt az ID-t kapja).

### 4. Post normalizálás

**Döntés:** A Google News posztok ugyanazt a dict struktúrát kapják mint a Reddit/HUP posztok:
```python
{
    'id': 'gnews-a1b2c3d4e5',
    'title': 'Leépítés jön a győri Audinál',
    'subreddit': 'google-news',      # kompatibilitás
    'source': 'google-news',
    'news_source': 'Portfolio.hu',    # a tényleges portál
    'date': '2026-01-14',
    'created_utc': 1736841600.0,
    'score': 0,                       # nincs upvote
    'num_comments': 0,                # nincs komment
    'url': 'https://news.google.com/rss/articles/...',
    'selftext': '',                   # nincs body
    'top_comments': [],
}
```

**Miért:** A pipeline többi része (analyzer, LLM validator, report) változatlanul tud dolgozni. A `score: 0` és `num_comments: 0` azt jelenti, hogy az engagement statisztikák természetesen a Reddit posztokat fogják dominálni — ez helyes viselkedés.

### 5. Source display

**Döntés:** A `_source_str()` függvény a reportban:
- Reddit: `r/{subreddit}` (nem változik)
- HUP: `hup.hu` (nem változik)
- Google News: `{news_source}` (pl. "Portfolio.hu", "HVG", "Telex")

**Miért:** A felhasználó számára az eredeti portál neve az informatív, nem az hogy "google-news".

## Risks / Trade-offs

- **Google News RSS elérhetetlenné válhat vagy rate limitálhat** → Graceful degradation: ha a fetch fail-el, log warning és skip, mint a HUP.hu scrapernél. A Google News modul izolált.
- **Selftext hiánya csökkenti az LLM validáció pontosságát** → A hír címek általában informatívabbak mint a Reddit címek (újságírói stílus), az LLM validáció cím alapján is jól tud dönteni.
- **Zajosabb eredmények (nem IT leépítés)** → A meglévő keyword-based analyzer és LLM validáció kiszűri a nem releváns híreket.
- **pubDate parse eltérések** → Az RSS `pubDate` szabványos RFC 2822 formátum, `email.utils.parsedate_to_datetime` stdlib-bel parsolható.
