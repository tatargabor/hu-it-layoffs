## Context

Az `src/llm_validator.py` jelenleg kizárólag a GitHub Models API-t használja (gpt-4o-mini, Azure endpoint). Ez ingyenes, de erős rate limiting van: 429-es hibák exponenciális backoff-fal, ami a 107 releváns poszt validálásánál többnyire timeout-ol. Egy teljes futás nem lehetséges ezzel a backenddel.

A gépen NVIDIA GPU van (CUDA 11.8), tehát helyi modell futtatás lehetséges.

## Goals / Non-Goals

**Goals:**
- Ollama backend támogatás az LLM validátorba
- Konfigurálható backend választás (GitHub vs Ollama)
- Rate limiting kikapcsolása helyi backend esetén
- Ugyanaz az output formátum mindkét backend esetén

**Non-Goals:**
- Nem cél más helyi LLM frameworkök (vLLM, llama.cpp közvetlenül) támogatása — Ollama elég
- Nem cél a prompt módosítása — ugyanaz a system prompt mindkét backendnél
- Nem cél automatikus modell letöltés/telepítés

## Decisions

### 1. Ollama OpenAI-kompatibilis API

Az Ollama `/v1/chat/completions` endpointot biztosít, ami az OpenAI API-val kompatibilis. Ezért a meglévő `_call_llm` függvény minimális módosítással használható — csak az URL-t és az auth header-t kell cserélni.

Alternatíva: Ollama natív API (`/api/chat`) — feleslegesen különböző, az OpenAI-kompatibilis API egyszerűbb.

### 2. Backend választás env var-ral

`LLM_BACKEND=ollama` vagy `LLM_BACKEND=github` (alapértelmezett: `github`). Ha `ollama`, az URL `http://localhost:11434/v1/chat/completions`, nincs auth header, nincs rate limit delay.

Alternatíva: CLI flag `--backend` a run.py-ben — túl bonyolult ehhez, env var egyszerűbb és a meglévő `GITHUB_TOKEN` mintát követi.

### 3. Modell választás

`LLM_MODEL` env var. Alapértelmezett: `gpt-4o-mini` (github) vagy `llama3.1` (ollama). Az Ollama JSON mode-ot támogat `"format": "json"` paraméterrel.

### 4. Nincs delay helyi backend esetén

A `REQUEST_DELAY` 0-ra áll Ollama esetén — nincs rate limit, felesleges lassítani.

## Risks / Trade-offs

- [Helyi modell minőség] A helyi modellek (llama3, mistral) gyengébbek lehetnek a gpt-4o-mini-nél magyar szöveg feldolgozásában → A confidence score jól szűr, és újra lehet futtatni gpt-4o-mini-vel ha elérhető
- [Ollama nem fut] Ha az Ollama szerver nem fut, a validáció sikertelen → Egyértelmű hibaüzenet: "Ollama not running at localhost:11434"
- [GPU memória] Nagy modellek nem férnek el a GPU-n → Alapértelmezett modell (llama3.1 8B) kis VRAM igényű
