## ADDED Requirements

### Requirement: Mobil stat kártyák layout
A dashboard stat kártyái mobilon (<=768px) SHALL 2 oszlopos gridet használjanak. A primary stat kártya SHALL teljes szélességben jelenjen meg (grid-column: 1 / -1).

#### Scenario: Stat kártyák mobilon
- **WHEN** a képernyő szélessége <= 768px
- **THEN** a stat kártyák 2 oszlopos gridben jelennek meg
- **THEN** a primary (leépítési jelzés) kártya teljes szélességet kap

### Requirement: Táblázatok horizontális scroll
A dashboard táblázatai mobilon SHALL horizontálisan scrollolhatók legyenek a tartalom levágása helyett.

#### Scenario: Széles táblázat mobilon
- **WHEN** egy táblázat szélesebb mint a viewport
- **THEN** a táblázat horizontálisan scrollolható egy wrapper elemen belül
- **THEN** a többi tartalom NEM scrollozódik vele

### Requirement: Chart container scroll mobilon
A horizontal bar chart containerek mobilon SHALL max-height limitet és overflow-y: auto scrollt kapjanak.

#### Scenario: Hosszú chart mobilon
- **WHEN** egy horizontal bar chart magasabb mint 450px és a képernyő <= 768px
- **THEN** a chart container scrollolható legyen vertikálisan
- **THEN** a chart összes adata elérhető legyen scrollal
