## Context

A jelenlegi pipeline: `raw_posts → analyzer.py (keyword) → llm_validator.py (egyenként) → report.py`. A keyword filter 71%-ot szűr ki statikus szólistával — ez a fő bottleneck, mert sok releváns poszt el sem jut az LLM-hez. Az AI attribution szintén keyword-alapú és csak 9/366 posztot talál, miközben legalább 24 releváns.

Az LLM backend már kétféle: GitHub Models (gpt-4o-mini, ingyenes) és Ollama (lokális). Mindkettő OpenAI-kompatibilis API-t használ.

## Goals / Non-Goals

**Goals:**
- Batch LLM triage: 1 hívás az összes cím szűrésére (~6k token)
- LLM-alapú AI attribution: `ai_role` mező (direct/factor/concern/none) + kontextus
- Keyword filter megmarad fallback-ként (offline/no-LLM mód)
- ~60-70% több releváns poszt a reportban

**Non-Goals:**
- Keyword listák bővítése (felesleges ha LLM triage van)
- Report/dashboard vizualizáció módosítása (az majd külön change)
- Új LLM backend bevezetése

## Decisions

### 1. Batch triage: egyetlen hívás vs egyenként

**Választás**: Egyetlen hívás az összes címmel.

Indoklás: 366 cím ~6k token — bőven elfér egy hívásban (128k context). Egyetlen hívás ~3 sec vs 366 × 0.5s = ~3 perc. A válasz JSON tömb sorszámokkal: `[3, 7, 15, ...]`.

Alternatíva elvetett: Egyenként hívás (366×) — lassú, drága, felesleges.

### 2. Triage prompt: sorszámok vs ID-k

**Választás**: Sorszámok (1-based index).

Indoklás: A Reddit post ID-k rövidek de kryptikusak ("t3_1abc2de"). Sorszámozás egyértelmű, rövidebb output, kevesebb token. A mapping `enumerate(posts)` alapján triviális.

### 3. Triage válasz formátum: JSON tömb

**Választás**: `{"relevant": [1, 5, 12, ...]}` JSON objektum.

Indoklás: Strukturált output, parseolható, támogatja mindkét backend JSON mode-ját. Alternatíva (vesszővel elválasztott szám-string) kevésbé robosztus.

### 4. AI attribution: 4 szintű skála

**Választás**: `direct` / `factor` / `concern` / `none` (a korábbi boolean `ai_attributed` helyett).

Indoklás: A "Szállás Group AI által megoldott fejlesztések" != "Megéri programozónak tanulni AI miatt?" — különböző súly, különböző riport-szekció. 4 szint ezt differenciálja.

### 5. Pipeline sorrend

**Választás**: `analyze → batch_triage → full_validate → report`

```
src/run.py módosított flow:

  raw_posts.json
       │
  ┌────▼────┐
  │ analyze │  keyword scoring (fallback data)
  └────┬────┘
       │
  ┌────▼──────────┐
  │ batch_triage  │  1× LLM hívás, összes cím
  │ (új függvény) │  → triage_relevant mező
  └────┬──────────┘
       │ ha LLM fail → keyword fallback
  ┌────▼──────────┐
  │ validate_posts│  N× LLM hívás (csak triage_relevant)
  │ (módosított)  │  + ai_role mező
  └────┬──────────┘
       │
  ┌────▼────┐
  │ report  │
  └─────────┘
```

### 6. Backward compatibility

A `validate_posts()` megkapja az opcionális `triage_results` paramétert. Ha nincs (régi hívás), a régi `relevance >= 1` logika működik. Az `llm_ai_role` és `llm_ai_context` mezők opcionálisak — a report `llm_ai_role` meglétét ellenőrzi mielőtt használná.

## Risks / Trade-offs

- **[LLM triage tévedhet]** → A triage inkább bőven szűr (false positive OK), a full validation majd finomít. Ha mégis kiesik poszt: keyword fallback is fut, ami minimum-hálóként működik.
- **[Batch hívás token limit]** → 366 cím ~6k token, 128k context limit mellett ez nem gond. Ha >5000 poszt lenne, batch-eket kell csinálni.
- **[Extra LLM hívás költség]** → +1 hívás/futás (~6k token), GitHub Models-en ingyenes, Ollama-n lokális. Elhanyagolható.
- **[JSON parse hiba batch válaszban]** → Retry 1×, ha sikertelen → keyword fallback.
