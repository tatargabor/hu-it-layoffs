## Why

A jelenlegi keyword-alapú szűrő (`analyzer.py`) a 366 posztból 259-et (71%) kiszűr relevance=0-val, és ezek **soha nem jutnak el az LLM-hez** — holott közöttük egyértelműen releváns posztok vannak (pl. "Manapság diplomával is nehéz IT-ban elhelyezkedni", "DevOps/SRE piac", "Az IT fejvadászok hogy nem halnak éhen??"). Emellett az AI attribution keyword-alapú detekciója csak 9 posztot talál, miközben az LLM summary-kben 15 további poszt is AI-t említ. A statikus szólista nem képes szemantikus megértésre.

## What Changes

- **Batch LLM triage lépés bevezetése**: Egyetlen LLM hívásban (~6k token) az összes poszt címét megvizsgáljuk — releváns-e az IT munkaerőpiac szempontjából. Ez váltja ki a keyword-alapú relevance szűrést mint elsődleges gate.
- **Keyword filter fallback-ké degradálása**: Ha nincs LLM elérhető (nincs token, nincs Ollama), a keyword filter továbbra is működik mint graceful degradation.
- **LLM-alapú AI attribution**: A full validation lépésben az LLM explicit mezőben jelzi az AI/automatizáció szerepét (nem csak keyword matching). Új `ai_role` mező a válasz-sémában.
- **Pipeline átrendezése**: raw → batch triage (LLM) → full validation (LLM) → report, keyword filter csak fallback.

## Capabilities

### New Capabilities
- `batch-triage`: Egyetlen LLM hívásban az összes poszt címének relevancia-szűrése (igen/nem az IT munkaerőpiac szempontjából)
- `llm-ai-attribution`: LLM-alapú AI/automatizáció szerep-detekció a full validation részeként, keyword-alapú helyett

### Modified Capabilities
- `llm-validator`: Pipeline módosítás — batch triage integráció, `ai_role` mező hozzáadása a válasz-sémához, keyword filter fallback logika

## Impact

- **src/llm_validator.py**: Új `batch_triage()` függvény, módosított `validate_posts()` flow, bővített SYSTEM_PROMPT (`ai_role` mező)
- **src/analyzer.py**: `_score_relevance()` és `_detect_ai_attribution()` megmarad fallback-ként, de nem elsődleges
- **src/run.py**: Pipeline sorrend módosítás (triage → full validation)
- **data/validated_posts.json**: Új mezők (`llm_ai_role`, `triage_relevant`)
- Költség: +1 LLM hívás/futás (~6k token, ingyenes GitHub Models/Ollama-val)
