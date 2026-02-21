## Why

A GitHub Models API (gpt-4o-mini) rate limiting (429) teljesen megakadályozza a teljes pipeline futtatását — 107 posztból 44-et sikerült validálni, a többi mindig timeout-ol. Helyi LLM backend kell, ami korlátlanul futtatható.

## What Changes

- Helyi Ollama backend támogatás az LLM validátorba (pl. llama3, mistral, gemma2)
- OpenAI-kompatibilis API hívás Ollama felé (`http://localhost:11434/v1/chat/completions`)
- Backend választás konfigurálható: `--backend github` (alapértelmezett) vagy `--backend ollama`
- Modell kiválasztás: `--model` flag (alapért: `gpt-4o-mini` GitHub-hoz, `llama3` Ollama-hoz)
- Rate limiting eltávolítása helyi backend esetén (nincs szükség delay-re)

## Capabilities

### New Capabilities
- `local-llm-backend`: Ollama-alapú helyi LLM validáció — OpenAI-kompatibilis API hívások localhost felé, konfiguráció, modell választás

### Modified Capabilities

## Impact

- `src/llm_validator.py`: Backend absztrakció, új Ollama hívási útvonal
- `src/run.py`: CLI argumentumok backend/modell választáshoz
- Függőség: Ollama telepítve kell legyen a gépen (nem Python dependency)
