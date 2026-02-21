## 1. LLM Validator — sector mező

- [x] 1.1 SYSTEM_PROMPT JSON séma bővítése `sector` mezővel (zárt lista: fintech, automotive, telecom, big tech, IT services, entertainment, energy, retail tech, startup, government, general IT, other, null) + példák frissítése
- [x] 1.2 `validate_posts()` — `llm_sector` mező mentése a poszt dict-be (`post['llm_sector'] = result.get('sector')`)
- [x] 1.3 `validate_posts()` — sector nélküli `llm_validated=True` posztok újra-validálási logika (ne ugorja át ha nincs `llm_sector`)

## 2. Report — szektor fallback lánc

- [x] 2.1 `report.py` — `_eff_sector(post)` helper: llm_sector → company_sector → "ismeretlen" fallback
- [x] 2.2 `report.py` — "Szektorok szerinti megoszlás" blokk (sor ~198-207) átírás `_eff_sector()` használatára
- [x] 2.3 `report.py` — "Érintett Cégek" tábla szektor oszlop (sor ~161) átírás `_eff_sector()` használatára
- [x] 2.4 `report.py` — "Cég típus" statisztika (sor ~314-318) átírás: sector-alapú csoportosítás (multi/startup/közepes/állami/nem besorolható)

## 3. Vizualizáció — szektoros chart

- [x] 3.1 `visualize.py` — szektoros chart adatforrás (sor ~108-111) átírás: llm_sector → company_sector → ismeretlen fallback lánc

## 4. Módszertan és költségbecslés

- [x] 4.1 `report.py` — módszertan szekció (sor ~383-419) újraírás: batch triage, szektor klasszifikáció, multi-backend dokumentálás
- [x] 4.2 `report.py` — költségbecslés szekció (sor ~422-435): llm_stats dict-ből dinamikus backend név és árazás, hardcoded gpt-4o-mini árak eltávolítása

## 5. Validálás

- [ ] 5.1 Teljes pipeline futtatás (`python src/run.py`) — ellenőrzés hogy llm_sector mező megjelenik a validated_posts.json-ban
- [ ] 5.2 Report ellenőrzés — szektorizálás arány javulás (cél: 50%+ a jelenlegi 19% helyett)
