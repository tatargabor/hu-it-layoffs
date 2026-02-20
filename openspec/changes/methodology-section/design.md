## Context

A report.py generálja a markdown-ot, a visualize.py a HTML dashboardot. Mindkettő a validated_posts.json és llm_stats.json alapján dolgozik. A módszertani szekciót statikus szövegként + dinamikus statisztikákkal kell generálni.

## Goals / Non-Goals

**Goals:**
- Módszertani szekció a report végén (md + html)
- Adatforrások, keresési lekérdezések, elemzési lépések leírása
- LLM validáció módszer és korlátok
- Dinamikus statisztikák beágyazása (poszt szám, validált szám, stb.)

**Non-Goals:**
- Nem cél külön methodology.md fájl — a reportba épül be
- Nem cél többnyelvű tartalom

## Decisions

### 1. A szekció a report végére kerül
A legfontosabb adatok (timeline, cégek) maradnak elöl. A módszertan kiegészítő információ, a végén olvasható.

### 2. HTML-ben összecsukható `<details>` elem
Nem foglal helyet alapból, de kinyitható. Nem kell JavaScript.

### 3. Statikus szöveg + dinamikus számok
A szöveg nagy része fix (módszertan nem változik), de a számok (posztszám, validált, futási idő) a stats dict-ből jönnek.

## Risks / Trade-offs

- [Magyar szöveg karbantartás] A módszertani szöveg hardcoded a Python fájlokban → Elfogadható, ritkán változik
