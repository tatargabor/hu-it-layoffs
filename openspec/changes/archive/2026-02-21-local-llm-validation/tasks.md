## 1. Backend absztrakció

- [x] 1.1 `_call_llm` refaktor: backend config dict bevezetése (url, headers, delay) a `LLM_BACKEND` és `LLM_MODEL` env varok alapján
- [x] 1.2 Ollama API hívás: `http://localhost:11434/v1/chat/completions`, auth header nélkül, `"format": "json"` paraméterrel
- [x] 1.3 Rate limit delay kikapcsolása Ollama backend esetén (`REQUEST_DELAY = 0`)

## 2. Hibakezeles és fallback

- [x] 2.1 Ollama elérhetőség ellenőrzése induláskor (connection test a `/v1/models` endpointra)
- [x] 2.2 Egyértelmű hibaüzenet ha Ollama nem fut: "Ollama not reachable at localhost:11434"

## 3. Tesztelés

- [x] 3.1 Teljes pipeline futtatás `LLM_BACKEND=ollama` beállítással a 107 releváns poszton
- [x] 3.2 Output ellenőrzés: `llm_validated`, `llm_relevance`, `llm_company` mezők megvannak és helyes struktúrájúak
