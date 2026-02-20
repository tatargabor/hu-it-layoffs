## Why

A riport jelenleg csak a posztok számát mutatja kategóriánként, de nem méri az engagement-et (upvote, komment). Az explore session során kiderült, hogy a freeze posztok átlagosan 131 kommentet generálnak — messze a legtöbbet. Ez egy kulcsfontosságú mérőszám, ami megmutatja, mennyire foglalkoztatja az embereket a téma.

## What Changes

- **Engagement összefoglaló szekció** a report.md-ben: összesített score + komment, kategóriánkénti bontás
- **Top posztok reakció szerint** tábla a reportban (score és komment top 5-5)
- **Engagement szekció a HTML dashboardban**: vizuális megjelenítés táblázatokkal
- **Negyedéves engagement trend** a timeline-ban: score + komment oszlopok hozzáadása

## Capabilities

### New Capabilities

_(nincs — meglévő report/dashboard bővítés)_

### Modified Capabilities

- `report-generation`: Engagement mérőszámok szekció hozzáadása a markdown riporthoz
- `dashboard-visualization`: Engagement megjelenítés a HTML dashboardon

## Impact

- `src/report.py`: Új engagement szekció generálás, timeline tábla bővítés
- `src/visualize.py`: Engagement szekció a HTML-ben
- `data/report.md`, `data/report.html`: Generált output bővül
