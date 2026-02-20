## Context

A pipeline 3 forrásból gyűjt (Reddit, HUP.hu, Google News). A Google News `hl=hu&gl=HU` paramétere magyar nyelvű cikkeket ad vissza, de ezek gyakran globális híreket tárgyalnak (Amazon USA leépítés, Ubisoft Torontó, Nestlé Svájc). Az LLM validátor promptja nem kérdezi a magyar vonatkozást és nem vizsgálja, hogy IT pozíciók érintettek-e — egy bolti eladó kirúgása vagy egy dél-koreai AI leépítés is `category=layoff, relevance=3`-at kap.

Jelenlegi állapot: 312 releváns posztból ~119 (51%) nem-magyar, és további ~30 nem-IT leépítés (Heineken, textilipar, barkácsáruház stb.).

## Goals / Non-Goals

**Goals:**
- LLM prompt-ban `hungarian_relevance` és `it_positions_affected` mezők → pontos szűrés
- Triage prompt erősítése: magyar vonatkozás + IT specifikusság kiemelés
- `_map_relevance()` csökkentse a nem-magyar és nem-IT posztok relevancia-értékét
- Report és vizualizáció szűrjön az új mezőkre
- Meglévő validált posztok újra-validálása (nincs rajtuk az új mező)

**Non-Goals:**
- Google News query-k szűkítése — a query-k jók, a szűrés LLM szinten kell
- Scraper módosítás — a scraper begyűjt mindent, a szűrés a validátorban történik
- Visszamenőleges adat-törlés — a posztok megmaradnak, csak a relevancia csökken

## Decisions

### 1. Két új mező a SYSTEM_PROMPT JSON sémában

```json
{
  "hungarian_relevance": "direct|indirect|none",
  "hungarian_context": "magyarázat vagy null"
}
```

- `direct`: Magyarországon történik, magyar céget érint, magyar munkavállalók érintettek (OTP, Ericsson Budapest, Szállás Group)
- `indirect`: Globális cég de van ismert magyar jelenlét, vagy a hír kifejezetten megemlíti a magyar hatást (pl. "Continental globális leépítés, Budapestet is érinti")
- `none`: Semmi magyar vonatkozás (Amazon USA, Ubisoft Torontó, dél-koreai AI)

**Miért nem boolean:** Az `indirect` kategória fontos — egy Continental globális leépítés releváns lehet ha van budapesti fejlesztőközpont. Boolean-nal ezt elveszítenénk.

### 2. IT pozíció vizsgálat — nem új mező, hanem prompt és mapping erősítés

Az `it_positions_affected` logikát a meglévő `category` + `sector` mezőkbe integráljuk:
- Ha a szektor nem-IT (retail, élelmiszer, textil, agrár) ÉS a pozíciók nem IT-sek → `category=other`
- A prompt példákat kap erre: "bolti eladó kirúgás = other", "áruházlánc leépítés = other (hacsak nem IT pozíciók)"

**Miért nem külön mező:** A `category=other` már pontosan ezt jelenti ("nem IT munkaerőpiac"). A prompt erősítése elég, nem kell új mező — kevesebb mező = olcsóbb és megbízhatóbb LLM output.

### 3. `_map_relevance()` módosítás

```python
def _map_relevance(llm_result):
    hungarian = llm_result.get('hungarian_relevance', 'direct')

    # Nem-magyar posztok max relevance = 1
    if hungarian == 'none':
        return 0

    # Indirect magyar: max relevance = 2
    category = llm_result.get('category')
    confidence = llm_result.get('confidence', 0.0)

    if category == 'layoff' and confidence >= 0.7:
        base = 3
    elif category in ('layoff', 'freeze'):
        base = 2
    elif category == 'anxiety':
        base = 1
    else:
        base = 0

    if hungarian == 'indirect' and base > 2:
        base = 2

    return base
```

### 4. Triage prompt erősítés

A TRIAGE_SYSTEM_PROMPT-ba belekerül:
- "CSAK magyar vonatkozású posztokat jelölj relevánsnak"
- "Globális tech cég leépítés (Amazon, Google, Meta) CSAK akkor releváns, ha kifejezetten magyar hatást említ"
- "Nem-IT szektorok (élelmiszer, textil, barkács, agrár) leépítései NEM relevánsak — KIVÉVE ha IT/tech pozíciókat érintenek"

### 5. Újra-validálás trigger

A `validate_posts()` logikában: ha `llm_validated=True` de `hungarian_relevance` mező hiányzik → újra-validálni (mint a sector nélküli posztoknál).

## Risks / Trade-offs

- **[False negative: indirect posztok]** → Egy Continental globális leépítés releváns lehet ha budapesti is érint, de az LLM nem biztos hogy tudja. → Mitigation: `indirect` kategória + a prompt kéri hogy ha kétes, jelölje indirect-nek.
- **[Prompt hossz növekedés]** → Két új mező + példák növelik a token-számot. → Mitigation: Minimális — 2 mező + 3-4 példasor, ~200 token.
- **[Újra-validálás költség]** → Minden meglévő `llm_validated` posztot újra kell futtatni. → Mitigation: Egyszer kell, utána inkrementális.
