## 1. LLM Prompt módosítás

- [x] 1.1 `SYSTEM_PROMPT` JSON sémájába `category` mező hozzáadása (`layoff`/`freeze`/`anxiety`/`other`) definíciókkal és példákkal minden kategóriára
- [x] 1.2 A meglévő prompt-példák frissítése: a `layoff` példa mellé `freeze` és `anxiety` példa is

## 2. Relevancia-mapping átírás

- [x] 2.1 `_map_relevance()` átírása kategória-alapúra: layoff+high→3, layoff+low→2, freeze→2, anxiety→1, other→0
- [x] 2.2 Fallback logika: ha nincs `category` kulcs az LLM eredményben, régi `is_actual_layoff` alapú mapping fut

## 3. Kategória mentés

- [x] 3.1 `validate_posts()` loop-ban `post['llm_category']` mező mentése az LLM válaszból

## 4. Validáció

- [x] 4.1 Pipeline újrafuttatás Ollama-val (`LLM_BACKEND=ollama python3 src/run.py`) és ellenőrzés: a report több posztot tartalmaz-e
