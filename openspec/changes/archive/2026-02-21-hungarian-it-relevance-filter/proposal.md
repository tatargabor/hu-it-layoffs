## Why

A releváns posztok ~51%-a nem magyar vonatkozású (Amazon USA, Ubisoft Torontó, Nestlé globális), és további posztok nem-IT szektorú leépítések (bolti eladó kirúgás, Heineken gyári leépítés, textilipar). Ezek azért csúsznak át, mert: (1) a Google News `hl=hu` magyar NYELVŰ cikkeket ad, nem magyar VONATKOZÁSÚAKAT, (2) az LLM prompt nem kéri a földrajzi és IT-specifikusság vizsgálatát. Eredmény: a riport fele zaj.

## What Changes

- LLM validátor prompt: két új mező — `hungarian_relevance` (direct/indirect/none) és `it_positions_affected` (true/false)
- LLM triage prompt: magyar vonatkozás és IT-specifikusság kiemelése a szűrési kritériumokban
- Report/vizualizáció: szűrés `hungarian_relevance != "none"` és `it_positions_affected == true` alapján
- Relevancia mapping: `hungarian_relevance=none` vagy `it_positions_affected=false` → automatikusan alacsony relevancia (0-1)

## Capabilities

### New Capabilities
- `hungarian-relevance-filter`: Magyar vonatkozás és IT pozíció szűrő — LLM prompt bővítés, relevancia mapping módosítás, report/vizualizáció szűrés

### Modified Capabilities

## Impact

- `src/llm_validator.py` — SYSTEM_PROMPT és TRIAGE_SYSTEM_PROMPT bővítés, `_map_relevance()` módosítás, új mezők mentése
- `src/report.py` — szűrés hungarian_relevance és it_positions_affected alapján
- `src/visualize.py` — szűrés az új mezőkre
- Újra-validálás szükséges az új mezők kitöltéséhez
