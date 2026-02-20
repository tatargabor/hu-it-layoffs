## Why

A report két helyen elavult: (1) a szövegek "Reddit posztok" forrást említenek mindenhol, holott már 3 forrás van (Reddit, HUP.hu, Google News), (2) a markdown report 1416 soros, ennek 79%-a három ismétlődő poszt-lista (Érintett Cégek, Részletes Táblázat, Források) — ez a README.md-t is olvashatatlanná teszi. A HTML dashboard amúgy is jobb ezekre, a markdown-nak elég az összesítés + link az adatokra.

## What Changes

- **Forrás szövegek frissítése:** "Reddit publikus adatok" → multi-source (Reddit, Google News, HUP.hu) mindenhol (report.py, visualize.py)
- **Módszertan frissítése:** Google News RSS és HUP.hu scraper leírás hozzáadása, nem csak Reddit
- **MD report rövidítés:** Részletes Táblázat, Források szekciók eltávolítása az MD-ből — helyettük link a `data/` könyvtárra és a HTML dashboardra. Érintett Cégek max top 20 + "további N cég a dashboardon"
- **Disclaimer frissítés:** multi-source megfogalmazás

## Capabilities

### New Capabilities
- `report-multi-source`: Report és vizualizáció multi-source frissítés + MD rövidítés

### Modified Capabilities

## Impact

- `src/report.py` — forrás szövegek, metodika szekció, MD rövidítés (Részletes Táblázat és Források eltávolítás, Cégek limit)
- `src/visualize.py` — header, disclaimer, módszertan szövegek frissítése multi-source-ra
