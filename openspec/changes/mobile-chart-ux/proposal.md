## Why

A dashboardra érkezett user feedback: (1) a horizontal bar chartok (cégek, technológiák, munkakörök) olvashatatlanok — 3x annyi gridline van mint label, mert Chart.js `autoSkip` kihagyja a labeleket de a gridline-ok maradnak; (2) a mobil UX használhatatlan — a chartok és táblázatok nem skálázódnak jól kis képernyőre, a tartalom struktúra nehezen átlátható.

## What Changes

- **Chart gridline fix**: Y-axis gridline-ok kikapcsolása horizontal bar chartoknál, dinamikus chart magasság (items × fix px) a statikus 350px helyett
- **Top N limit**: Cég/tech/role chartok limitálása top 15-re (jelenleg az összes adat megjelenik, ami 37+ cég esetén olvashatatlan)
- **Mobil responsive javítások**: chart containerek horizontális scrollja mobilon, stat kártyák 2-oszlopos grid mobilon, táblázatok horizontális scroll wrapper, nagyobb touch target-ek
- **Content struktúra**: stat kártyák prioritás szerinti rendezés mobilon, chart-box-ok közötti spacing javítás

## Capabilities

### New Capabilities
- `mobile-responsive`: Mobil-specifikus layout és interakció szabályok (breakpointok, scroll viselkedés, touch target-ek)

### Modified Capabilities
- `dashboard-visualization`: Chart rendering szabályok változnak (gridline kezelés, dinamikus magasság, top N limit)
- `html-visualizer`: CSS media query-k bővülése, chart container viselkedés mobilon

## Impact

- `src/visualize.py` — Chart.js opciók módosítása, CSS media query-k bővítése, chart HTML/JS generálás
- Nincs backend/pipeline változás — csak a `generate_html()` output változik
- Meglévő `validated_posts.json`-ból azonnal újragenerálható, pipeline futtatás nem szükséges
