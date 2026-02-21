## 1. Forrás szövegek frissítése

- [x] 1.1 `src/report.py` — header sor: "Forrás: Reddit publikus adatok" → "Forrás: Reddit, Google News, HUP.hu publikus adatok"
- [x] 1.2 `src/report.py` — disclaimer szöveg: "publikusan elérhető Reddit posztok" → "publikusan elérhető posztok és hírek" (magyar + angol)
- [x] 1.3 `src/visualize.py` — header subtitle: "Reddit (r/programmingHungary, r/hungary)" → "Reddit, Google News, HUP.hu publikus adatok"
- [x] 1.4 `src/visualize.py` — disclaimer szöveg: "Reddit posztok" → "posztok és hírek" (magyar + angol)

## 2. Módszertan frissítése

- [x] 2.1 `src/report.py` — Módszertan/Adatgyűjtés: Google News RSS (`hl=hu&gl=HU`) és HUP.hu fórum scraping leírás hozzáadása
- [x] 2.2 `src/report.py` — Pipeline lépés 1: "Reddit JSON API" → "Multi-source scraping (Reddit, Google News RSS, HUP.hu)"
- [x] 2.3 `src/visualize.py` — Módszertan: ugyanazok a frissítések mint report.py-ban (Google News + HUP.hu leírás, pipeline lépés)

## 3. MD report rövidítés

- [x] 3.1 `src/report.py` — Részletes Táblázat szekció törlése, helyette: "Részletes adatok az [Interaktív Dashboard-on](link)"
- [x] 3.2 `src/report.py` — Források poszt-lista szekció törlése, helyette link `data/validated_posts.json`-ra
- [x] 3.3 `src/report.py` — Érintett Cégek: max 20 sor, utána "További N cég → [dashboard link]"
- [x] 3.4 `src/report.py` — Közösségi Engagement, Hiring Freeze részletes lista, Technológiák, Munkakörök szekciók törlése az MD-ből (dashboardon maradnak)
- [x] 3.5 `src/report.py` — Trend Elemzés rövidítés: cég típus részletezés törlése, AI-attribúció és trend sor marad
