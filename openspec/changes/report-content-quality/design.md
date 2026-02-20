## Context

A pipeline: `scraper → analyzer → batch_triage (LLM) → validate_posts (LLM) → report → visualize`. Az LLM promptok jelenleg nem szűrik az IT szektorra a tartalmat — bármilyen leépítés relevancia 3-at kap. A `visualize.py` AI countja nem használja az LLM `ai_role` mezőt, csak a keyword-alapú `ai_attributed`-ot.

Konkrét példák a jelenlegi tévesztésekre:
- Magyar Honvédség katonai átszervezése → layoff, relevancia 3
- Corvinus nyelvtanárok elbocsátása → layoff, relevancia 3
- MATE agrár kutatóintézet bezárása → layoff, relevancia 3
- "Junior Frontend fejlesztőnek tanács?" → layoff, relevancia 3 (egyéni tanácskérés)

## Goals / Non-Goals

**Goals:**
- LLM promptok IT/tech szektorra fókuszálása — nem-IT leépítések `other` kategóriát kapjanak
- Személyes tanácskérés posztok max relevancia 2 (nem "közvetlen leépítés")
- AI count szinkronizálása visualize.py és report.py között
- Névtelen/általános entitások kiszűrése a cégstatisztikákból

**Non-Goals:**
- Új LLM backend bevezetése
- Pipeline strukturális változtatás (a jelenlegi triage → validate flow marad)
- Dashboard UI/layout módosítás

## Decisions

### 1. Prompt módosítás stratégia

**Választás**: Kategória-definíciók pontosítása a meglévő SYSTEM_PROMPT-ban.

Indoklás: Nem kell új prompt vagy új lépés — elég a `category` és `is_actual_layoff` definíciókat szigorítani az IT szektorra. A triage prompt maradhat bőkezű (ez szűrő, jobb ha több jut át), de a validation prompt-ban a kategorizálás legyen pontos.

### 2. IT szektor definiálása a promptban

**Választás**: Explicit lista + heurisztika a SYSTEM_PROMPT-ban.

```
IT/tech szektor = szoftverfejlesztés, IT szolgáltatás, telekommunikáció,
tech cégek, IT osztályok más szektorban (pl. OTP IT, Audi IT).

NEM IT: katonai, oktatási (kivéve IT képzés), agrár, közlekedés,
gyártás (kivéve tech gyártás), kiskereskedelem (kivéve tech cégek).
```

### 3. Relevancia szintek pontosítása

**Választás**: `is_actual_layoff` definíció szigorítása + új `is_it_sector` mező.

Jelenlegi probléma: az LLM `is_actual_layoff: true`-t ad minden leépítésre, szektortól függetlenül.

Új logika a SYSTEM_PROMPT-ban:
- `is_actual_layoff: true` → csak IT szektorban, szervezeti szintű leépítésnél
- Egyéni "kirúgtak és tanácsot kérek" → `is_actual_layoff: false`, `category: anxiety` vagy `freeze`
- Nem-IT leépítés → `category: other`, bármilyen szektor

A `_eff_relevance()` mapping nem változik (`is_actual_layoff` → 3, `category == layoff` → 2, stb) — a prompt pontosítás elég.

### 4. AI count fix a dashboard-ban

**Választás**: `_is_ai_attributed()` helper bevezetése a `visualize.py`-ba, azonos logikával mint `report.py`.

```python
def _is_ai_attributed(post):
    if post.get('llm_validated') and 'llm_ai_role' in post:
        return post['llm_ai_role'] in ('direct', 'factor', 'concern')
    return post.get('ai_attributed', False)
```

3 helyen kell cserélni a `visualize.py`-ban: stat card ai_count, AI trend chart, detailed table ai_str.

### 5. Cégszűrés stratégia

**Választás**: Általános/névtelen entitások kiszűrése a cégszám-statisztikából.

Szabály: cég csak akkor számít "érintett cégnek" ha:
- Konkrét, azonosítható cégnév (nem "nagyobb német cég", nem "magyar élelmiszerlánc")
- Nem egyéni vállalkozó / freelancer hivatkozás

Implementáció: egyszerű filter a company set-re mindkét fájlban.

## Risks / Trade-offs

- **[Prompt módosítás revalidálást igényel]** → Az LLM újra kell validálja a posztokat. Ez ~370 sec Anthropic-on, de a CI pipeline amúgy is napi futtatás.
- **[Esetleg túl sokat szűr]** → Ha egy IT-s leépítés nem IT cégben történik (pl. bank IT osztály), azt a prompt "más szektorban lévő IT osztály" kitétellel kezeli.
- **[Backward compatibility]** → Az `is_it_sector` mező opcionális, régi adatban nem lesz benne. A report kód fallback-el: ha nincs `is_it_sector`, a régi logika fut.
