## Why

A dashboard és a markdown report nem tartalmaz módszertani leírást. Egy külső olvasó nem tudja, hogyan készült az adat: milyen forrásokból, milyen szűréssel, milyen AI validációval. Ez csökkenti a hitességet és a hivatkozhatóságot.

## What Changes

- Új "Módszertan" szekció a markdown reportba (`data/report.md`) — adatgyűjtés, elemzés, LLM validáció leírása, korlátok
- Ugyanez a HTML dashboardba (`data/report.html`) — összecsukható/kinyitható szekció
- A szekció automatikusan generálódik a `src/report.py` és `src/visualize.py` által

## Capabilities

### New Capabilities
- `methodology-content`: Módszertani szekció generálása — adatforrások, keresési lekérdezések, relevancia pontozás, LLM validáció leírása, korlátok, hivatkozások

### Modified Capabilities

## Impact

- `src/report.py`: Új szekció hozzáadása a markdown generátorhoz
- `src/visualize.py`: Új szekció a HTML dashboardba (összecsukható panel)
- `data/report.md`, `data/report.html`: Kibővített kimenet
