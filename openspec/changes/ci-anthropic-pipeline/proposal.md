## Why

A GitHub Models API (gpt-4o-mini) rate limiting (HTTP 429) megakadályozza a teljes pipeline automatikus futtatását — ~107 posztból max 44-et tud validálni mielőtt timeout. A lokális Ollama backend megoldás fejlesztéshez, de CI automatizáláshoz megbízható, fizetős API kell. Az Anthropic Haiku 4.5 kiváló magyar szövegértéssel rendelkezik, nincs érdemi rate limit, és ~$0.04/futás költséggel üzemeltethető.

## What Changes

- Új LLM backend: `anthropic` — natív Anthropic Messages API (`/v1/messages`) támogatás a `llm_validator.py`-ban
- Új GitHub Actions workflow (`pipeline.yml`): napi cron-futtatás a teljes scrape → analyze → LLM → report pipeline-hoz
- A pipeline végén `git commit + push data/` ami triggereli a meglévő Pages deploy workflow-t
- A meglévő `github` és `ollama` backend-ek megmaradnak (lokális fejlesztéshez)
- Env var alapú konfiguráció: `LLM_BACKEND=anthropic`, `ANTHROPIC_API_KEY` secret

## Capabilities

### New Capabilities
- `anthropic-backend`: Anthropic Messages API backend a meglévő LLM validator-hoz (Haiku 4.5 modell, natív API, nem OpenAI-kompatibilis)
- `ci-pipeline`: GitHub Actions workflow napi automatikus pipeline futtatáshoz Anthropic API-val

### Modified Capabilities

_(nincs meglévő főspec módosítás — a v2-ci-llm-validation még nem lett szinkronizálva főspec-be)_

## Impact

- **Kód**: `src/llm_validator.py` — új `anthropic` backend branch a `_resolve_backend()` és `_call_llm()` függvényekben
- **CI**: Új `.github/workflows/pipeline.yml` workflow
- **Secrets**: `ANTHROPIC_API_KEY` repo secret szükséges a GitHub repo Settings-ben
- **Költség**: ~$0.04/futás × 30 nap = ~$1.2/hó
- **Meglévő kód**: A `github` és `ollama` backend-ek változatlanok maradnak
