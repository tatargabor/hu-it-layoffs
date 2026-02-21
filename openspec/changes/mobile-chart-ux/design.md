## Context

A dashboard `src/visualize.py` egy ~860 soros Python fájl, ami Chart.js 4.4.7-tel generál interaktív HTML reportot. A chartok jelenleg:
- **Company chart**: horizontal bar, `indexAxis: 'y'`, az összes cég (37+), 350px max-height → Chart.js `autoSkip` kihagyja a labeleket de gridline-ok maradnak
- **Tech/Roles chart**: hasonlóan horizontal bar, top 15/10
- **Mobil**: egyetlen `@media (max-width: 768px)` rule — 1 oszlopos grid, de semmi más adaptáció

A HTML egy monolitikus f-string a `generate_html()` függvényben — CSS, HTML és JS mind inline.

## Goals / Non-Goals

**Goals:**
- Gridline/label konzisztencia javítása horizontal bar chartokon
- Cég chart limitálása top 15-re (jelenleg korlátlan)
- Mobil UX javítása: olvasható chartok, scrollolható táblázatok, jobb spacing
- Stat kártyák mobil layout (2×4 grid a jelenlegi auto-fit helyett)

**Non-Goals:**
- Chart library csere (Chart.js marad)
- Adat vagy pipeline változtatás
- Desktop UX redesign
- Tablet-specifikus breakpoint (768px marad a breakpoint)
- Dark/light mode

## Decisions

### 1. Gridline kezelés: grid kikapcsolás vs. label force-display
**Döntés**: Y-axis grid kikapcsolása (`scales.y.grid.display: false`) + minden label megjelenítése (`scales.y.ticks.autoSkip: false`)

Alternatíva: `ticks.maxTicksLimit` használata — de ez Chart.js-re bízza melyik labelt hagyja ki, ami nem intuitív. A grid kikapcsolás tisztább, mert a horizontal bar-ok önmaguk vizuális elválasztók.

### 2. Chart magasság: dinamikus vs. fix
**Döntés**: Dinamikus magasság — `Math.max(items * 28, 200)` px, CSS max-height eltávolítása az érintett canvas-oknál

A 350px fix magasság 37 cégnél = ~9.5px/bar ami olvashatatlan. Dinamikussal 37 × 28 = 1036px, ami scrollolható a chart-box-ban.

### 3. Chart container scroll: overflow-y vs. CSS max-height a canvas-on
**Döntés**: A chart-box kap `max-height: 450px; overflow-y: auto` mobilon, desktopnál nincs limit. A canvas maga nem kap max-height-ot.

Alternatíva: a canvas-on tartani a max-height-ot — de ez Chart.js-nél torzít, mert a lib a container alapján számol.

### 4. Top N limit cég chartnál
**Döntés**: Top 15 cég a chartban (jelenleg az összes). A Python oldalon történik a slice, nem JS-ben.

A többi cég a táblázatból továbbra is elérhető. 15 cég × 28px = 420px ami jól elfér.

### 5. Mobil stat kártyák
**Döntés**: `grid-template-columns: repeat(2, 1fr)` mobilon az `auto-fit, minmax(180px, 1fr)` helyett. A primary stat (leépítési jelzés) marad `grid-column: 1 / -1` teljes szélességben.

### 6. Mobil táblázatok
**Döntés**: Táblázat wrapper div `overflow-x: auto` -val. Ez natív horizontális scroll-t ad mobilon.

## Risks / Trade-offs

- **Hosszú chart scroll mobilon** → A 15 cég limit csökkenti ezt, de tech (15) + roles (10) chartok is lehetnek hosszúak. Elfogadható mert scrollolható container-ben vannak.
- **Canvas max-height eltávolítás desktop hatása** → Csak a horizontal bar chartoknál (company, tech, roles) távolítjuk el a limitet, a timeline és doughnut chartoknál marad.
