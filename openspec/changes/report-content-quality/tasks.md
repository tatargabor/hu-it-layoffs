## 1. LLM Prompt IT-szektorra fókuszálás

- [x] 1.1 Módosítani a `TRIAGE_SYSTEM_PROMPT`-ot (`src/llm_validator.py` sor 15-35): "Releváns" és "NEM releváns" listákhoz hozzáadni az IT/tech szektor szűrőt — nem-IT szektorok leépítései nem relevánsak, kivéve ha IT pozíciókat érintenek
- [x] 1.2 Módosítani a `SYSTEM_PROMPT`-ot (`src/llm_validator.py` sor 37-93): `category: layoff` definíciót szűkíteni IT/tech szektorra, `is_actual_layoff` definíciót szűkíteni szervezeti szintű leépítésre (nem egyéni tanácskérés)
- [x] 1.3 Hozzáadni negatív példákat a SYSTEM_PROMPT few-shot részéhez: Honvédség → other, Corvinus nyelvtanárok → other, egyéni "kirúgtak tanácsot kérek" → freeze/anxiety (nem layoff)

## 2. Dashboard AI count fix

- [x] 2.1 `_is_ai_attributed()` helper hozzáadása a `src/visualize.py`-hoz (azonos logika mint `src/report.py` sor 39-43)
- [x] 2.2 Cserélni 3 helyen a `visualize.py`-ban: stat card ai_count (sor ~137), AI trend chart (sor ~86), detailed table ai_str (sor ~169) — `p.get('ai_attributed')` → `_is_ai_attributed(p)`

## 3. Cégszűrés

- [x] 3.1 `_is_named_company()` helper hozzáadása `src/report.py`-hoz és `src/visualize.py`-hoz — kiszűri a névtelen/általános entitásokat ("nagyobb német cég", "magyar élelmiszerlánc")
- [x] 3.2 Alkalmazni a szűrőt a company set számításnál mindkét fájlban

## 4. Újravalidálás és ellenőrzés

- [ ] 4.1 Pipeline újrafuttatás az új prompt-okkal (teljes revalidáció)
- [ ] 4.2 Ellenőrzés: Honvédség, Corvinus, MATE, akkugyárak → `other` kategória
- [ ] 4.3 Ellenőrzés: Szállás Group → AI-érintett a dashboardon is
- [ ] 4.4 Ellenőrzés: érintett cégszám csökkent (nincs benne "nagyobb német cég" stb)
- [ ] 4.5 Ellenőrzés: "közvetlen leépítés" szám csökkent (tanácskérések kiestek)
