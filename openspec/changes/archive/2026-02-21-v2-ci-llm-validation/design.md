## Context

A v1 pipeline (scraper → analyzer → report) működik és produkált adatot: ~200 poszt, 32KB markdown riport, 19KB HTML dashboard. A kulcsszó-alapú scoring azonban pontatlan — egy "van leépítés az X cégnél?" típusú kérdés is relevance 3-at kap. A pipeline manuális futtatást igényel, az eredmények nem publikáltak.

Jelenlegi fájlstruktúra:
- `src/scraper.py` — Reddit JSON API scraper
- `src/analyzer.py` — kulcsszó-alapú elemzés
- `src/report.py` — markdown report generátor
- `src/visualize.py` — HTML dashboard (Chart.js)
- `src/run.py` — pipeline orchestrator (nem hívja a visualize.py-t)

A projekt stdlib-only policy-t követ (nincs pip install, csak urllib/json).

## Goals / Non-Goals

**Goals:**
- LLM-mel validálni a kulcsszó-alapú scoring-ot (pontosabb relevancia, cég, létszám)
- Automatikus napi 2x futtatás GitHub Actions-ből
- Publikus HTML dashboard GitHub Pages-en
- Report layout javítás (létszám first, részletes táblázat)

**Non-Goals:**
- Új adatforrások (HWSW, Prohardver) — külön change-ben
- Saját LLM hosting / fine-tuning
- Felhasználói felület a dashboardon túl (nincs login, nincs szerkesztés)
- Valós idejű frissítés (batch job elég)

## Decisions

### D1: LLM provider — GitHub Models API (gpt-4o-mini)

**Választás:** GitHub Models (`models.inference.ai.azure.com`), gpt-4o-mini modell.

**Miért nem más:**
- Gemini Flash: ingyenes, de külön API key kell GitHub secret-ként
- Claude Haiku: jobb magyarul, de ~$12/hó költség
- Groq/Llama: ingyenes, de magyar nyelv gyengébb
- Lokális LLM: GPU kell, CI-ben nem praktikus

**Előny:** A `GITHUB_TOKEN` automatikusan elérhető minden Actions workflow-ban — nulla konfigurációval működik. Lokálisan `gh auth token`-nel szerezhető.

### D2: Token resolution chain

```
1. os.environ['GITHUB_TOKEN']           → CI-ben automatikus
2. subprocess(['gh', 'auth', 'token'])  → lokális fejlesztéshez
3. None → skip LLM, kulcsszó-scoring marad (graceful degradation)
```

Ha nincs token, a pipeline nem törik el — a régi scoring megmarad, és egy warning jelzi hogy LLM validáció nem futott.

### D3: LLM validáció mint külön pipeline lépés

A validátor a `data/analyzed_posts.json`-t olvassa és egy `data/validated_posts.json`-t ír. Nem módosítja az analyzer-t, hanem utána fut és felülírja/kiegészíti a mezőket.

```
Scraper → Analyzer (kulcsszó) → LLM Validator → Report
                                      │
                              data/validated_posts.json
                              (vagy analyzed_posts.json ha skip)
```

Mezők az LLM-től:
- `llm_validated`: bool
- `llm_relevance`: 0-3 (felülírhatja a kulcsszó-alapút)
- `llm_company`: str|null
- `llm_headcount`: int|null
- `llm_confidence`: 0.0-1.0
- `llm_summary`: str (1 mondat, magyarul)

A report a `llm_relevance`-t használja ha van, egyébként a régi `relevance`-t.

### D4: Batch processing rate limit kezelés

GitHub Models free tier: 150 req/perc, 300K token/nap. ~200 poszt × ~500 token ≈ 100K token.

Stratégia: szekvenciális feldolgozás, 0.5s delay requestek között. Nem kell batch API — a szekvenciális is belefér 2 perc alatt.

Csak relevancia >= 1 posztokat validálunk (a 0-sokat kihagyjuk — azok egyértelműen nem relevánsak).

### D5: GitHub Actions workflow

```yaml
schedule: "0 6,18 * * *"  # UTC 6:00 és 18:00 (magyar 7:00 és 19:00)
```

Lépések:
1. Checkout
2. Setup Python (stdlib, nincs pip)
3. Run pipeline (`python -m src.run`)
4. Commit `data/` + `README.md` changes
5. Push
6. GitHub Pages deploy (HTML)

A `data/raw_posts.json` és `data/analyzed_posts.json` is commitolódik — átláthatóság fontosabb mint a méret (a git jól tömöríti a JSON diffeket).

### D6: README.md generálás

A `report.md` tartalmát másoljuk `README.md`-be egy header-rel kiegészítve (link a live dashboard-ra). Így a GitHub repo főoldala maga a riport.

### D7: Report layout — létszám first

A HTML dashboard stat card-ok sorrendje:
1. Becsült érintett létszám (legnagyobb, kiemelt szín)
2. Közvetlen leépítés
3. Releváns posztok
4. Érintett cégek
5. AI-t említő posztok
6. Hiring freeze

Új section: "Részletes Táblázat" — `<details>` tag-ben az összes poszt (nem csak top 30).

## Risks / Trade-offs

**[GitHub Models rate limit elérése]** → A 150 RPM és 300K token/nap bőven elég ~200 poszthoz. Ha a posztszám 1000+ fölé nő (több forrás), batch-olni kell. Monitoring: a validator loggolja a felhasznált tokenszámot.

**[GitHub Models API változás/megszűnés]** → A graceful degradation biztosítja hogy a pipeline LLM nélkül is fut. Az LLM validáció opcionális réteg, nem core dependency.

**[Git repo méret növekedés]** → Napi 2x commit ~3MB JSON-nel. Évi ~2GB. Elfogadható egy adat-repóhoz. Ha gond lesz: git-lfs vagy artifact-only.

**[gpt-4o-mini magyar nyelvi pontossága]** → Jó, de nem tökéletes. A prompt-ban explicit magyar nyelvű válaszokat kérünk és few-shot példákat adunk. Ha a minőség nem elég: fallback Claude Haiku-ra (drágább de pontosabb).

**[GitHub Pages deploy versenyhelyzet]** → Ha két workflow egyszerre fut (manuális + cron), conflict lehet. A workflow `concurrency` group-pal kezeli.
