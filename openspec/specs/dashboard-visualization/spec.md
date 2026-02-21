## ADDED Requirements

### Requirement: Engagement szekció a HTML dashboardon
A HTML dashboard SHALL tartalmazzon egy "Közösségi Engagement" szekciót a kategóriánkénti engagement táblával és a top posztok listájával.

#### Scenario: Engagement szekció megjelenik a dashboardon
- **WHEN** a HTML dashboard generálódik
- **THEN** a dashboard tartalmaz egy engagement szekciót az összesített és kategóriánkénti engagement adatokkal

### Requirement: Engagement összefoglaló kártyák
A dashboard összefoglaló kártyái között SHALL megjelenjen az összes reakció (score + komment).

#### Scenario: Engagement kártyák a dashboard tetején
- **WHEN** a dashboard generálódik 2782 össz score-ral és 2737 össz kommenttel
- **THEN** a summary kártyák között megjelenik az engagement adat
