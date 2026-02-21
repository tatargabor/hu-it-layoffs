## Context

A dashboard audit 154 "Top Posts" elemből 50-et (32%) talált problémásnak. A zaj három rétegből ered:

1. **Karriertanács posztok (27 db)**: "Junior álláskeresés", "CV tippek", "Merre menjek" — ezek az IT álláspiac hangulatjelzői, de nem leépítési események. Az LLM relevancia 2-t adott rájuk és category='other'.
2. **Generikus AI doom cikkek (6 db)**: "300 millió munkahely szűnik meg az AI miatt" — clickbait, konkrét cég/esemény nélkül.
3. **Nem-IT szektor leépítések (15 db)**: Magyar Posta, Rail Cargo, RTL, Operaház, Tesco, Aldi — valós leépítések, de nem IT szektor. Némelyik átjutott mert az LLM sector-nak "government" vagy "entertainment"-et adott, ami nem volt a `_NON_IT_SECTORS` halmazban.

Jelenlegi szűrési rétegek:
```
Keyword scoring (0-3) → LLM batch triage → LLM full validation → _eff_relevance >= 2 → _is_hungarian_relevant → _is_it_relevant → Dashboard
```

A probléma: az LLM validáció és a post-filter réteg között nincs elég szigorú szűrés.

## Goals / Non-Goals

**Goals:**
- A dashboard kizárólag IT szektorhoz köthető leépítési/freeze eseményeket mutasson
- Karriertanács és generikus AI cikkek ne jelenjenek meg a fő listán
- Nem-IT szektor leépítések kiszűrése (hacsak nem IT pozíciókat érint)
- Meglévő, valóban releváns posztok megmaradnak

**Non-Goals:**
- A "Részletes Táblázat" (összes releváns poszt) szűrését NEM változtatjuk — az marad mint van
- Nem írjuk át az LLM validáció teljes struktúráját
- Nem változtatjuk a relevancia pontozási skálát (0-3)

## Decisions

### 1. Kétszintű megközelítés: LLM prompt + post-filter

**Döntés:** Mindkét réteget javítjuk, nem csak egyiket.

**Miért:** Az LLM prompt javítás a forrásánál kezel sok problémát (karriertanács → rel 1, AI doom → rel 1), de az LLM nem 100%-os, ezért a post-filter is kell mint biztonsági háló.

**Alternatíva:** Csak post-filter — elutasítva, mert a prompt javítás sokkal finomabb kontextus-értékelést tud.

### 2. Blacklist → Whitelist váltás (`_NON_IT_SECTORS` → `_IT_SECTORS`)

**Döntés:** A blacklist megközelítés helyett whitelist-re váltunk. Az `_IT_SECTORS` halmaz tartalmazza az IT-releváns szektorokat: `fintech`, `big tech`, `IT services`, `telecom`, `startup`, `general IT`, `retail tech`. Minden más szektor (beleértve a jövőben megjelenő ismeretleneket) automatikusan nem-IT-ként kezelődik, és csak IT roles/techs mentions esetén jut át a szűrőn.

**Miért:** A blacklist folyamatos karbantartást igényelt volna — bármilyen új, ismeretlen szektor (pl. `agriculture`, `mining`) átjutott volna. A whitelist jövőbiztos: az IT szektorok stabil halmaz, amit az LLM sector enum-ja definiál (`llm_validator.py:50`).

**Alternatíva:** Blacklist bővítés — elutasítva az explore elemzés alapján, mert nem skálázódik.

### 3. Category filter a Top Posts táblára

**Döntés:** A Top Posts (relevancia >= 2) táblában kizárjuk a `category='other'` posztokat — csak `layoff`, `freeze`, `anxiety` marad.

**Miért:** A 27 karriertanács poszt mindegyike category='other'. Ez a leghatékonyabb szűrő a zaj legnagyobb részére.

### 4. Generikus AI cikk detekció — LLM-re bízva, regex biztonsági háló

**Döntés:** A generikus AI cikkek szűrését elsősorban az LLM prompt javítás (Döntés #5) végzi: `relevance: 1`-et kap → nem jut a Top Posts-ba. A `_is_specific_event()` függvényt NEM vezetjük be külön — a `category != 'other'` filter (Döntés #3) és az LLM prompt javítás együtt elegendő.

**Miért:** Az explore elemzés kimutatta, hogy a regex-alapú `_is_specific_event()` törékeny (★★☆☆☆ tartósság), magyar nyelvű mintákra építve folyamatos karbantartást igényelne. Az LLM prompt + category filter kombináció tartósan (★★★★★) kezeli ugyanezt a problémát.

### 5. LLM prompt frissítés

**Döntés:** A validátor prompt explicit instrukciókat kap:
- Karriertanács/álláskereső poszt → `relevance: 1` (még ha az IT szektort érinti is)
- Generikus AI munkaerőpiaci cikk konkrét cég/esemény nélkül → `relevance: 1`
- Nem-magyar vonatkozás → `hungarian_relevance: "none"`

**Miért:** A prompt-szintű kezelés sokkal pontosabb mint a post-filter, mert az LLM érti a kontextust.

### 6. Meglévő posztok invalidálása

**Döntés:** A prompt változás után a meglévő `llm_validated` posztokat NEM invalidáljuk automatikusan — a post-filter réteg elég a meglévő adatra. Csak az újonnan validált posztok kapják az új promptot.

**Miért:** Teljes re-validáció drága (~$2.50) és a post-filter már most kiszűri a problémás elemek többségét.

## Risks / Trade-offs

- **[Túl szigorú szűrés]** → A Magyar Posta IT leépítés (#77, #100) jogosan releváns (informatikusokat érintett). Megoldás: `_is_it_relevant()` továbbra is átengedi ha IT roles/techs mentioned.
- **[LLM prompt regression]** → Az új prompt esetleg más posztokat is alacsonyabbra pontozhat. Megoldás: csak specifikus instrukciókat adunk, nem változtatjuk az alap relevancia kritériumokat.
- **[Dashboard elemszám csökkenés]** → 154 → ~100 elem. Ez elfogadható, mert a kikerülő elemek nem IT leépítések.
