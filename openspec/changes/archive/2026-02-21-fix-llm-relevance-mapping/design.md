## Context

Az `llm_validator.py` jelenleg bináris döntést kér az LLM-től: `is_actual_layoff: true/false`. Az `_map_relevance()` ezt így fordítja le:
- `is_layoff=true, confidence>=0.8` → relevance 3
- `is_layoff=true, confidence>=0.5` → relevance 2
- `not is_layoff, confidence<0.7` → relevance 1
- minden más → relevance 0

A probléma: az Ollama a legtöbb "nem konkrét leépítés" posztra `is_actual_layoff=false, confidence=0.8-0.9` válaszol → relevance 0. Így 94/107 validált poszt kiesik.

Az `analyzer.py`-ban viszont már létezik egy jól működő 4 kategóriás rendszer: `layoff`, `freeze`, `anxiety`, `other`.

## Goals / Non-Goals

**Goals:**
- Az LLM is kategorizáljon a 4 kategória szerint (layoff/freeze/anxiety/other)
- A relevancia-mapping a kategóriát használja, ne csak a bináris `is_actual_layoff`-ot
- Visszafelé kompatibilis maradjon: régi validált adatok továbbra is működjenek

**Non-Goals:**
- A keyword-alapú analyzer logika módosítása (az marad ahogy van)
- A report.py `_eff_relevance()` módosítása (az már jó, az LLM relevancia-értéket használja)
- Újravalidálás automatizálása (kézzel kell futtatni)

## Decisions

### 1. LLM válasz-séma bővítése `category` mezővel

A `SYSTEM_PROMPT` JSON sémája kiegészül:
```json
{
  "is_actual_layoff": true/false,
  "category": "layoff|freeze|anxiety|other",
  "confidence": 0.0-1.0,
  ...
}
```

A `category` mező definíciói a promptban:
- `layoff`: Konkrét elbocsátás, leépítés, létszámcsökkentés
- `freeze`: Hiring freeze, álláspiac-romlás, nehéz elhelyezkedés, felvételi stop
- `anxiety`: Karrier-aggodalom, bizonytalanság, kiégés, pályaváltás kérdések a szektorra vonatkozóan
- `other`: Nem releváns (általános kérdés, hír, offtopic)

**Alternatíva**: Külön `is_market_signal` mező — elvetettük, mert a 4 kategória már létezik az analyzerben és konzisztensebb.

### 2. `_map_relevance()` kategória-alapú mapping

Új logika:
```
category=layoff, confidence>=0.7  → relevance 3
category=layoff, confidence>=0.4  → relevance 2
category=freeze                   → relevance 2
category=anxiety                  → relevance 1
category=other                    → relevance 0
```

Fallback: ha nincs `category` mező (régi adat), a jelenlegi `is_actual_layoff` alapú logika fut.

### 3. `llm_category` mező mentése a validált posztokba

Az LLM válaszból a `category` értéket `post['llm_category']`-ként mentjük, hasonlóan a többi `llm_*` mezőhöz.

## Risks / Trade-offs

- **[Ollama kategória pontossága]** → Az Ollama kisebb modell, lehet hogy a 4-es kategorizálás kevésbé pontos mint a bináris. Mitigation: a prompt példákat ad minden kategóriára.
- **[Backward compat]** → Régi validated_posts.json-ben nincs `category` mező. Mitigation: `_map_relevance()` fallback a régi `is_actual_layoff` logikára ha nincs category.
- **[Túl sok poszt visszakerül]** → A lazább szűrés esetleg irreleváns posztokat is beenged. Elfogadható trade-off: jobb ha több van mint ha kevesebb.
