## 1. Chart Gridline és Label Fix

- [x] 1.1 Company chart: `scales.y.grid.display: false` és `scales.y.ticks.autoSkip: false` hozzáadása a Chart.js options-höz (`src/visualize.py` ~805. sor)
- [x] 1.2 Tech chart: ugyanaz a gridline/label fix a tech chart JS-ben (`tech_chart_js` változó)
- [x] 1.3 Roles chart: ugyanaz a gridline/label fix a roles chart JS-ben (`roles_chart_js` változó)

## 2. Top N Limit és Dinamikus Magasság

- [x] 2.1 Company chart: `top_companies` slice top 15-re a Python oldalon (jelenleg korlátlan)
- [x] 2.2 Canvas `max-height: 350px` CSS eltávolítása, helyette dinamikus magasság: a horizontal bar chart canvas-ok height attribútumát `Math.max(items * 28, 200)` alapján számolni JS-ben
- [x] 2.3 Chart-box containerekhez `overflow-y: auto` hozzáadása a horizontal bar chart típusoknál

## 3. Mobil Responsive CSS

- [x] 3.1 Stat kártyák: `@media (max-width: 768px)` blokkban `.stats { grid-template-columns: repeat(2, 1fr) }` és `.stat.primary { grid-column: 1 / -1 }`
- [x] 3.2 Táblázatok: wrapper div `overflow-x: auto`-val a table-section-ökben és a details táblánál
- [x] 3.3 Chart containerek: mobilon `max-height: 450px; overflow-y: auto` a horizontal bar chart-box-okra

## 4. Tesztelés és Regenerálás

- [x] 4.1 HTML újragenerálás meglévő adatokból (`generate_html()` hívás `validated_posts.json`-nal)
- [ ] 4.2 Vizuális ellenőrzés: desktop és mobil nézet (chartok, táblázatok, stat kártyák)
