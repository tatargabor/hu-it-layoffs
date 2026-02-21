## Why

A dashboard audit feltárta, hogy a 154 "Top Posts" elemből **50 (32%) nem felel meg az "IT Leépítés" kritériumnak**. A zaj három fő forrásból ered: (1) karriertanács/álláskereső posztok amelyek nem leépítésről szólnak, (2) generikus "AI elveszi a munkát" cikkek konkrét esemény nélkül, (3) nem-IT szektorok leépítései (posta, vasút, áruházlánc, operaház, TV). Ez rontja a dashboard hitelességét és a felhasználói élményt.

## What Changes

- **Report-szintű szűrő szigorítás**: A `category='other'` posztok kizárása a "Top Posts" (relevancia >= 2) táblából — csak `layoff`, `freeze`, `anxiety` kategóriák maradnak
- **IT szektor whitelist**: `_NON_IT_SECTORS` blacklist helyett `_IT_SECTORS` whitelist — csak az ismert IT szektorok (`fintech`, `big tech`, `IT services`, `telecom`, `startup`, `general IT`, `retail tech`) jutnak át, minden más szektor csak IT roles/techs mention esetén. Jövőbiztos: ismeretlen szektorok automatikusan kiszűrődnek.
- **Generikus AI cikk kezelés**: LLM prompt hangolás + category filter kombináció kezeli — nincs külön regex-alapú `_is_specific_event()` függvény
- **Magyar relevancia szigorítás**: Külföldi leépítések (Szlovákia, Románia, globális) kiszűrése, ha nincs magyar vonatkozás
- **LLM prompt hangolás**: A validációs prompt frissítése — explicit instrukció, hogy karriertanács/álláskereső posztok max relevancia 1-et kapjanak, generikus AI cikkek szintén

## Capabilities

### New Capabilities
- `relevance-post-filter`: Report/dashboard szintű post-filter szabályok amelyek az LLM validáció után, a megjelenítés előtt további szűrést végeznek (kategória, szektor, AI-doom detekció, magyar relevancia)

### Modified Capabilities
_(nincs meglévő spec módosítás)_

## Impact

- `src/report.py` — `_NON_IT_SECTORS` bővítés, `_is_it_relevant()` szigorítás, "Top Posts" szűrő hozzáadás
- `src/visualize.py` — ugyanazok a szűrők mint report.py
- `src/llm_validator.py` — prompt frissítés a karriertanács és AI-doom cikkek kezelésére
- `data/validated_posts.json` — meglévő posztok invalidálása a prompt változás miatt (a pipeline újra validálja)
- Dashboard elemszám ~154 → ~100-110 várhatóan a szűrés után
