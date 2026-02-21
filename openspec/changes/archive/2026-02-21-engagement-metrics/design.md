## Context

Az adatokban már megvan a `score` (upvote) és `num_comments` minden poszthoz. Ezt jelenleg csak a részletes táblázatban mutatjuk, de nincs összesítés, nincs engagement szekció.

Az explore session adatai:
- 51 releváns poszt összesen 2782 score + 2737 komment
- Freeze posztok: átl. 131 komment/poszt (legtöbb diskurzus)
- Layoff posztok: átl. 101 score/poszt (legtöbb upvote)
- Anxiety: átl. 33 score, 47 komment (sok poszt, mérsékelt engagement)

## Goals / Non-Goals

**Goals:**
- Engagement összefoglaló a riport tetején (summary szekcióban)
- Kategóriánkénti engagement tábla
- Top 5 poszt score és top 5 poszt kommentszám szerint
- Negyedéves timeline bővítése score + komment oszlopokkal
- HTML dashboardon engagement megjelenítés

**Non-Goals:**
- Engagement score képlet kitalálása (egyszerűen score + komment külön)
- Engagement alapú ranking/súlyozás (a relevancia marad ami volt)
- Új adatgyűjtés (mindez már megvan a raw adatban)

## Decisions

### 1. Report.py: új "Közösségi Engagement" szekció

A "Összesített Statisztikák" szekció után, új szekció:
- Összesített: össz score, össz komment
- Kategóriánkénti tábla: | Kategória | Posztok | Össz score | Össz komment | Átl. score | Átl. komment |
- Top 5 score + Top 5 komment listák

### 2. Timeline tábla bővítés

A negyedéves timeline táblához 2 új oszlop: Score és Kommentek.

### 3. HTML dashboard: engagement kártya

A `visualize.py`-ban új szekció az összefoglaló kártyák között + a kategória engagement tábla.

## Risks / Trade-offs

- **[Tábla szélesség]** → A timeline tábla 2 új oszloppal szélesebb lesz. Elfogadható, mert a lényeges adat.
- **[HTML komplexitás]** → Egy új szekció a dashboardon. Minimális növekedés.
