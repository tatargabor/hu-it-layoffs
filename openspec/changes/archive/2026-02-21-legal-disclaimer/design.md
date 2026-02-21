## Context

A report cégeket nevesít leépítési kontextusban Reddit posztok alapján. A tartalom harmadik féltől származik, de az aggregáció és megjelenítés a mi felelősségünk. Jogi védelemre van szükség rágalmazás, hírnévsértés és GDPR szempontból.

## Goals / Non-Goals

**Goals:**
- Egyértelmű disclaimer minden kimeneten (MD, HTML, repo)
- Jelzés hogy harmadik fél tartalma, nem ellenőrzött
- Eltávolítási kontakt (GitHub Issues)
- A disclaimer automatikusan generálódik a pipeline-ban

**Non-Goals:**
- Nem cél jogi tanácsadás — ez egy ésszerű disclaimer, nem helyettesíti az ügyvédi véleményt
- Nem cél cookie/privacy policy — nincs tracking, nincs felhasználói adat

## Decisions

### 1. Disclaimer a report elején, nem a végén
A cím után, az adatok előtt kell lennie — mielőtt bárki elolvassa a cégneveket.

### 2. HTML-ben a header részeként, nem külön
A dashboard header-be kerül, mindig látható, nem elrejthető.

### 3. Magyar + angol disclaimer
Magyar az elsődleges, de angol kiegészítés kell, mert nemzetközi cégek érintettek.

## Risks / Trade-offs

- [Nem teljes jogi védelem] A disclaimer nem garantálja a permentességet → Elfogadható, a legtöbb hasonló aggregátor ezt használja
- [Vizuális zaj] A disclaimer csökkenti az adatok vizuális hatását → Rövid, kompakt szöveg
