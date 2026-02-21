## Why

A v1 pipeline működik (scraper → analyzer → report), de a kulcsszó-alapú relevancia scoring pontatlan, a futtatás manuális, és az eredmények csak lokálisan érhetők el. LLM validációval a pontosság jelentősen javulna, GitHub Actions-szel automatizálva naponta friss adatunk lenne, GitHub Pages-szel pedig bárki megnézhetné az interaktív dashboardot.

## What Changes

- GitHub Actions workflow: napi 2x automatikus futtatás (scraper → analyzer → LLM validate → report), eredmények commitolása és GitHub Pages deploy
- LLM validációs lépés: GitHub Models API (gpt-4o-mini) strukturált JSON output-tal validálja a posztok relevancia scoring-ját, cég-azonosítást és létszám becslést
- Token resolution: `GITHUB_TOKEN` env var → `gh auth token` fallback → skip (graceful degradation)
- Report layout átrendezés: becsült érintett létszám kiemelése az elejére, részletes táblázat az összes posztról (collapsible HTML section)
- `run.py` kiegészítés: `visualize.py` hívása beépítve a pipeline-ba

## Capabilities

### New Capabilities
- `llm-validator`: GitHub Models API-n keresztül gpt-4o-mini validálja az analyzed posztokat — is_actual_layoff, confidence, company, headcount, summary mezőkkel. Token: env var → gh CLI fallback → skip.
- `ci-pipeline`: GitHub Actions workflow napi 2x cron-nal, data/ commitolás, GitHub Pages deploy a HTML reporthoz, README.md frissítés a markdown reporttal.

### Modified Capabilities
- `report-generator`: Layout átrendezés — létszám first, részletes táblázat hozzáadása (összes poszt, collapsible), LLM confidence overlay a chartokon
- `html-visualizer`: Részletes táblázat tab/section, LLM validated vs keyword-only vizuális megkülönböztetés, létszám chart prioritás
- `post-analyzer`: LLM validáció integrálása — ha van LLM eredmény, felülírja/kiegészíti a kulcsszó-alapú scoring-ot

## Impact

- Új fájlok: `.github/workflows/report.yml`, `src/llm_validator.py`
- Módosított fájlok: `src/run.py`, `src/report.py`, `src/visualize.py`, `src/analyzer.py`
- Új dependency: GitHub Models API (urllib-bel hívva, nincs pip install)
- GitHub repo szintű: Pages engedélyezés kell, `GITHUB_TOKEN` permissions: `contents: write`
- `README.md` automatikusan generálódik a report.md-ből
