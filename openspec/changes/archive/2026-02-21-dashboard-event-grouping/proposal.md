## Why

A dashboard listáiban (Top Posts, Részletes Táblázat) ugyanaz az esemény többször is megjelenik, mert több forrás is tudósít róla (pl. OTP 2026 Q1 leépítés = 8 poszt, Docler = 4, Szállás Group = 3). Ez zavaró és nehéz áttekinteni. Az `event_label` mező már létezik és az LLM validáció kitölti — 11 eseménynél van duplikáció (összesen 34 felesleges sor). A csoportosítás logikája kész, csak a megjelenítésből hiányzik.

## What Changes

- **Group** posts by `event_label` in Top Posts and Részletes Táblázat tables
- **Show** one representative row per event group (Reddit poszt preferált, ha van)
- **Collapsible** sub-rows: lenyitható a csoport, alatta a többi forrás
- **Badge** showing source count (pl. "3 forrás")
- **Apply** same grouping logic in markdown report company table

## Capabilities

### New Capabilities
- `event-grouping-ui`: Esemény-alapú csoportosítás a dashboard listáiban lenyitható sorokkal

### Modified Capabilities
_(No existing specs)_

## Impact

- `src/visualize.py`: Top Posts és Részletes Táblázat generálás átírása csoportosított megjelenítésre
- `src/report.py`: Company table csoportosítása (markdown-ban indent vagy összevonás)
- Nem kell új dependency
- Nem változik az adatformátum — kizárólag megjelenítési logika
