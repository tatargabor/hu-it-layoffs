## Why

80 erős posztból 65-nek (81%) "ismeretlen" a szektora. A szektor-hozzárendelés jelenleg csak 26 hardcoded cégnévre működik (`analyzer.py` KNOWN_COMPANIES), miközben az LLM validator már felismeri a cégneveket de szektort nem kér. Az LLM kontextusból még cégnév nélkül is tudna szektort adni (pl. "banki IT leépítés" → fintech). Emellett a módszertan szekció elavult, és a költségbecslés hardcoded gpt-4o-mini árakra épül.

## What Changes

- LLM validator prompt bővítése: új `sector` mező a structured output-ban (predefined kategóriák: fintech, automotive, telecom, big tech, IT services, entertainment, energy, retail tech, startup, government, general IT, other)
- Report generálás: `llm_sector` → `company_sector` → KNOWN_COMPANIES lookup → "ismeretlen" fallback lánc
- Vizualizáció: szektoros chart `llm_sector` támogatás
- Módszertan szekció: batch triage lépés, szektor-klasszifikáció, multi-backend (Ollama/Anthropic/GitHub Models) dokumentálás
- Költségbecslés: `llm_stats` dict-ből dinamikusan, nem hardcoded árak
- "Cég típus" statisztika: LLM sector alapú csoportosítás (multinational/startup/SME) a jelenlegi primitív logika helyett

## Capabilities

### New Capabilities
- `llm-sector-classification`: LLM-alapú szektor klasszifikáció — az LLM prompt-ban sector mező, sector fallback lánc a reportban és vizualizációban

### Modified Capabilities
- `llm-ai-attribution`: Módszertan szekció frissítése (batch triage, multi-backend, sector klasszifikáció dokumentálás)

## Impact

- `src/llm_validator.py` — SYSTEM_PROMPT bővítés + `llm_sector` mező mentés
- `src/report.py` — szektorizálási logika, módszertan szekció, költségbecslés, cég típus stat
- `src/visualize.py` — szektoros chart adatforrás
- Újra-validálás szükséges (LLM újrafuttatás) az `llm_sector` mező kitöltéséhez a meglévő posztokra
