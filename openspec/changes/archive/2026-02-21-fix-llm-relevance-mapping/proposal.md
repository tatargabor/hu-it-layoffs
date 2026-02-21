## Why

Az LLM validáció (`llm_validator.py`) túl szigorúan szűr: a 366 scrapelt posztból csak 13-at tart meg relevánsnak. Az `_map_relevance()` függvény csak a `is_actual_layoff=true` válaszokat értékeli, így az álláspiac-romlás, hiring freeze, karrier-aggodalom típusú posztok mind kiesnek (relevance=0). Ezek a kategóriák az `analyzer.py`-ban már definiáltak (`layoff`, `freeze`, `anxiety`, `other`), de az LLM prompt nem ismeri őket.

## What Changes

- **LLM prompt bővítése**: A `SYSTEM_PROMPT`-ban a válasz-séma kiegészül egy `category` mezővel (`layoff` / `freeze` / `anxiety` / `other`), ami az analyzer.py kategóriáival konzisztens
- **`_map_relevance()` átírása**: A kategória-alapú mapping bevezetése — `layoff` → relevance 3, `freeze` → relevance 2, `anxiety` → relevance 1, `other` → relevance 0
- **Visszamenőleges validáció**: A már validált posztokat nem kell újra futtatni, de az `_map_relevance` logika az új mezőt is kezelje fallback-kel

## Capabilities

### New Capabilities

_(nincs)_

### Modified Capabilities

- `llm-validation`: Az LLM prompt kategória-mezőt kap, a relevancia-mapping lazul a freeze/anxiety posztok megtartásáért

## Impact

- `src/llm_validator.py`: `SYSTEM_PROMPT`, `_map_relevance()`, esetleg `_call_llm()` JSON parsing
- `data/validated_posts.json`: Újrafuttatáskor az LLM válaszok `category` mezőt is tartalmaznak
- A report és dashboard automatikusan több posztot fog mutatni, mert `_eff_relevance()` az LLM-ből jövő magasabb relevancia-értékeket kapja
