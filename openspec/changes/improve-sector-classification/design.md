## Context

A riportban 80 erős posztból 65-nek (81%) "ismeretlen" a szektora. A jelenlegi rendszer:
1. `analyzer.py` — 26 hardcoded cégnévvel keres, ha talál → szektor a szótárból
2. `llm_validator.py` — LLM felismer cégeket (`llm_company`), de szektort nem kér
3. `report.py` — csak `company_sector`-t nézi (analyzer output), `llm_company`-t figyelmen kívül hagyja szektorizálásnál
4. `visualize.py` — szintén csak `company_sector`-t nézi a chart-hoz

Az LLM már 10 extra céget felismert amihez nincs szektor, és 55 poszt esetén cégnév sincs — de kontextusból az LLM szektort tudna mondani ("banki IT", "autógyári fejlesztők").

## Goals / Non-Goals

**Goals:**
- LLM prompt-ban `sector` mező → 80%+ szektorizálás a jelenlegi 19% helyett
- Report és vizualizáció használja az `llm_sector`-t
- Módszertan szekció tükrözze a tényleges pipeline-t (batch triage, multi-backend, szektor)
- Költségbecslés dinamikus legyen, ne hardcoded

**Non-Goals:**
- KNOWN_COMPANIES szótár bővítése — az LLM szektor ezt feleslegessé teszi hosszú távon
- Új vizualizációs chart típusok — csak az adat-forrás változik
- Scraper vagy batch triage módosítás

## Decisions

### 1. LLM prompt bővítés `sector` mezővel

Az LLM SYSTEM_PROMPT JSON sémája kiegészül:
```json
"sector": "fintech|automotive|telecom|big tech|IT services|entertainment|energy|retail tech|startup|government|general IT|other|null"
```

**Miért zárt lista:** Konzisztens csoportosítás a riporthoz. Az LLM a poszt kontextusából választ, nem kell hozzá cégnév.

**Miért null opció:** Ha a poszt tényleg nem ad elég kontextust (pl. "merre tovább az IT-ben?" — anxiety, nincs szektor).

**Alternatíva elvetése:** Szabad szöveg sector → túl sok variáció, nehéz aggregálni.

### 2. Szektor fallback lánc

```
llm_sector (ha llm_validated)
  → company_sector (ha analyzer talált)
    → "ismeretlen"
```

**Miért LLM first:** Az LLM a teljes kontextust látja (cím, szöveg, kommentek), míg az analyzer csak cégnév-lookup. Az LLM "fintech"-et mondhat egy "banki IT leépítés" posztra ahol cégnév nincs.

### 3. Módszertan szekció újraírás

A `report.py` módszertan szekciója jelenleg statikus szöveg. Frissítjük:
- Batch triage lépés dokumentálás
- Szektor klasszifikáció leírás
- Multi-backend megemlítés (Ollama/Anthropic/GitHub Models)
- Költségbecslés az `llm_stats` dict-ből, nem hardcoded

### 4. "Cég típus" statisztika javítás

Jelenlegi logika (`report.py:314-318`): "van szektor és nem startup" = multinacionális. Új logika:
- `big tech`, `telecom`, `automotive`, `energy` → Multinacionális/Nagyvállalat
- `startup`, `AI/startup` → Startup/KKV
- `fintech`, `IT services`, `retail tech`, `entertainment` → Közepes/vegyes
- `government` → Állami
- `general IT`, `other`, `ismeretlen` → Nem besorolható

## Risks / Trade-offs

- **[Re-validálás szükséges]** → Az `llm_sector` mező kitöltéséhez újra kell futtatni a validálást. Ez CI-ben automatikus, lokálisan `python src/run.py` kell. A meglévő `llm_validated=True` posztokat is újra kell validálni mert nincs rajtuk sector. → Mitigation: `validate_posts()` logikában a sector nélküli llm_validated posztokat is újra-validálni.
- **[LLM szektor pontossága]** → Az LLM nem mindig találja el a szektort, különösen ha a poszt nem nevez meg céget. → Mitigation: A zárt lista és a "general IT" catch-all csökkenti a hibás besorolást. Confidence score már van.
- **[Visszafelé kompatibilitás]** → Meglévő `company_sector` mező változatlan marad, az `llm_sector` új mező. Report a fallback láncot használja.
