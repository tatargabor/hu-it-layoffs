## ADDED Requirements

### Requirement: Engagement összefoglaló a summary szekcióban
A riport summary szekciója SHALL tartalmazza az összesített engagement számokat: összes score és összes kommentszám a releváns posztokra.

#### Scenario: Engagement számok megjelennek a summaryban
- **WHEN** a riport generálódik 51 releváns poszttal, összesen 2782 score-ral és 2737 kommenttel
- **THEN** a summary szekció tartalmazza: "Összes reakció: 2 782 upvote, 2 737 komment"

### Requirement: Kategóriánkénti engagement tábla
A riport SHALL tartalmazzon egy "Közösségi Engagement" szekciót, benne kategóriánkénti táblázattal: Kategória | Posztok | Össz score | Össz komment | Átl. score | Átl. komment.

#### Scenario: Engagement tábla kategóriánként
- **WHEN** a riport generálódik releváns posztokkal amiknek van llm_category-juk
- **THEN** a tábla soronként mutatja a layoff, freeze, anxiety kategóriákat engagement adatokkal

### Requirement: Top posztok reakció szerint
A riport SHALL tartalmazzon két listát: Top 5 poszt score szerint és Top 5 poszt kommentszám szerint.

#### Scenario: Top 5 score megjelenik
- **WHEN** a riport generálódik
- **THEN** a "Legtöbb reakció" lista az 5 legmagasabb score-ú releváns posztot mutatja címmel, score-ral és linkkel

#### Scenario: Top 5 komment megjelenik
- **WHEN** a riport generálódik
- **THEN** a "Legtöbb komment" lista az 5 legtöbb kommentet kapott releváns posztot mutatja

### Requirement: Negyedéves timeline engagement oszlopok
A negyedéves timeline tábla SHALL tartalmazzon Score és Komment oszlopokat is.

#### Scenario: Timeline tábla engagement oszlopokkal
- **WHEN** a negyedéves timeline tábla generálódik
- **THEN** minden negyedév sorában megjelenik az adott negyedév össz score-ja és össz kommentszáma
