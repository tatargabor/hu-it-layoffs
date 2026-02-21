## Context

A pipeline 3 forrásból gyűjt: Reddit (r/programmingHungary, r/hungary, r/Layoffs, r/cscareerquestions), Google News RSS (magyar nyelvű IT leépítés keresés), HUP.hu (fórum scraping). A report és vizualizáció szövegei még csak Reddit-et említenek. Az MD report 1416 soros, a README.md túl hosszú.

## Goals / Non-Goals

**Goals:**
- Minden szöveges hivatkozást multi-source-ra frissíteni (report.py + visualize.py)
- MD report rövidítés: ~200-300 sorra (összesítés + link dashboard-ra)
- Módszertan szekció: Google News RSS + HUP.hu leírás

**Non-Goals:**
- HTML dashboard változtatás (a táblázatok ott maradnak, az jó helyen van)
- Új szekciók hozzáadása
- Adatgyűjtés módosítása

## Decisions

### 1. MD report szekciók

**Marad (rövidítve):**
- Header + summary
- Negyedéves Timeline
- Érintett Cégek — **top 20**, utána "további N cég → [dashboard link]"
- Összesített Statisztikák
- Trend Elemzés (rövidítve)
- Módszertan (frissítve multi-source-ra)

**Törlődik az MD-ből:**
- Részletes Táblázat (403 sor) → link a dashboardra
- Források lista (403 sor) → link a `data/validated_posts.json`-ra
- Közösségi Engagement → dashboardon marad
- Hiring Freeze részletes lista → dashboardon marad
- Technológiák, Munkakörök listák → dashboardon marad

### 2. Forrás szövegek cseréje

| Helyen | Régi | Új |
|--------|------|-----|
| report.py header | "Forrás: Reddit publikus adatok" | "Forrás: Reddit, Google News, HUP.hu publikus adatok" |
| report.py disclaimer | "publikusan elérhető Reddit posztok" | "publikusan elérhető posztok és hírek" |
| visualize.py header | "Reddit (r/programmingHungary, r/hungary) publikus adatok" | "Reddit, Google News, HUP.hu publikus adatok" |
| visualize.py disclaimer | "publikusan elérhető Reddit posztok" | "publikusan elérhető posztok és hírek" |

### 3. Módszertan szekció frissítés

Hozzáadandó:
- **Google News RSS** — `hl=hu&gl=HU` paraméterű keresés, magyar nyelvű IT leépítés hírek
- **HUP.hu** — magyar tech fórum keresés
- Pipeline leírásban: "multi-source scraping" a Reddit-only helyett

## Risks / Trade-offs

- **[MD információ-vesztés]** A Részletes Táblázat és Források törlése csökkenti az MD önálló értékét. → Mitigation: link a HTML dashboardra és data/ könyvtárra.
- **[README rövidítés]** A README.md a report.md-ből generálódik — a rövidítés a README-t is javítja.
