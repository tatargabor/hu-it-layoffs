## 1. Post-filter szűrők (report.py + visualize.py)

- [x] 1.1 Cseréld le a `_NON_IT_SECTORS` blacklistet `_IT_SECTORS` whitelistre mindkét fájlban: `{'fintech', 'big tech', 'IT services', 'telecom', 'startup', 'general IT', 'retail tech'}`. Frissítsd `_is_it_relevant()` logikáját: `if sector not in _IT_SECTORS: → check IT roles`
- [x] 1.2 Frissítsd a Top Posts szűrőt mindkét fájlban: `_eff_relevance(p) >= 2` mellé add hozzá `_eff_category(p) != 'other'`
- [x] 1.3 Frissítsd a `generate_report()` `strong` listát ugyanezzel a category szűrővel

## 2. LLM prompt hangolás (llm_validator.py)

- [x] 2.1 A SYSTEM_PROMPT-ba add hozzá: karriertanács/álláskereső poszt → relevance: 1 max, category: "other"
- [x] 2.2 A SYSTEM_PROMPT-ba add hozzá: generikus AI munkaerőpiaci cikk konkrét cég/esemény nélkül → relevance: 1
- [x] 2.3 A TRIAGE_SYSTEM_PROMPT-ba add hozzá: karriertanács/álláskereső típusú címek → NEM releváns

## 3. Verify

- [x] 3.1 Generáld újra a riportot lokálisan és ellenőrizd: a karriertanács posztok eltűntek a Top Posts-ból
- [x] 3.2 Ellenőrizd: a nem-IT szektor leépítések kiszűrve (kivéve ahol IT roles/techs vannak)
- [x] 3.3 Ellenőrizd: a valóban releváns posztok (OTP, Ericsson, Docler, Szállás Group, Agoda) megmaradtak
- [x] 3.4 Számold meg az új Top Posts elemszámot — 244 → 162 (82 nem-IT/karriertanács eltávolítva)
