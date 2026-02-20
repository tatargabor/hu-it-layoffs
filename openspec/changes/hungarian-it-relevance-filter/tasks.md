## 1. LLM Validator — prompt bővítés

- [x] 1.1 SYSTEM_PROMPT JSON séma bővítése `hungarian_relevance` (direct/indirect/none) és `hungarian_context` mezőkkel + mező leírások hozzáadása
- [x] 1.2 SYSTEM_PROMPT példák bővítése: magyar vonatkozás nélküli globális cikk (→ none), indirect (→ indirect), bolti eladó/nem-IT leépítés (→ other)
- [x] 1.3 SYSTEM_PROMPT-ban nem-IT szektor leépítések kiemelése: retail bolti dolgozó, élelmiszer, textil, agrár → category=other (hacsak nem IT pozíciók)
- [x] 1.4 `validate_posts()` — `llm_hungarian_relevance` és `llm_hungarian_context` mezők mentése a poszt dict-be
- [x] 1.5 `validate_posts()` — `hungarian_relevance` nélküli `llm_validated=True` posztok újra-validálási trigger (ne ugorja át)

## 2. LLM Triage prompt erősítés

- [x] 2.1 TRIAGE_SYSTEM_PROMPT bővítése: "CSAK magyar vonatkozású IT posztokat jelölj relevánsnak"
- [x] 2.2 TRIAGE_SYSTEM_PROMPT: globális tech leépítés (Amazon, Google, Meta) CSAK akkor releváns ha magyar hatást említ
- [x] 2.3 TRIAGE_SYSTEM_PROMPT: nem-IT szektorok leépítései (élelmiszer, textil, barkács, agrár) NEM relevánsak, kivéve ha IT pozíciókat érintenek

## 3. Relevancia mapping

- [x] 3.1 `_map_relevance()` módosítás: `hungarian_relevance=none` → return 0, `indirect` → max 2 cap

## 4. Report és vizualizáció szűrés

- [x] 4.1 `report.py` — statisztikák és táblázatok szűrése: `hungarian_relevance != "none"` feltétel hozzáadása
- [x] 4.2 `visualize.py` — chart adatok szűrése: `hungarian_relevance != "none"` feltétel hozzáadása

## 5. Validálás

- [x] 5.1 Teljes pipeline futtatás (`python src/run.py`) — ellenőrzés hogy `hungarian_relevance` mező megjelenik a validated_posts.json-ban
- [x] 5.2 Ellenőrzés: globális posztok (Amazon, Ubisoft, Nestlé) relevancia alacsony (0-1), nem-IT posztok (bolti eladó) category=other
