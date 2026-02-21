## ADDED Requirements

### Requirement: Batch triage egyetlen LLM hívásban

A `batch_triage()` függvény SHALL egyetlen LLM hívásban megkapja az összes poszt címét számozott listaként, és SHALL visszaadja a releváns posztok sorszámait. A prompt SHALL meghatározza, hogy az IT munkaerőpiac szempontjából releváns posztokat keressük (leépítés, álláspiac-romlás, hiring freeze, karrier-szorongás, AI hatás a munkára).

#### Scenario: Batch triage egyértelmű IT leépítés posztra
- **WHEN** a címek között szerepel "Ericsson 200 embert bocsát el Budapesten"
- **THEN** a poszt sorszáma megjelenik a releváns listában

#### Scenario: Batch triage álláskereső nehézség posztra
- **WHEN** a címek között szerepel "Manapság diplomával is nehéz IT-ban elhelyezkedni"
- **THEN** a poszt sorszáma megjelenik a releváns listában

#### Scenario: Batch triage irreleváns posztra
- **WHEN** a címek között szerepel "Milyen monitort ajánlotok home office-hoz?"
- **THEN** a poszt sorszáma NEM jelenik meg a releváns listában

### Requirement: Batch triage prompt formátum

A prompt SHALL tartalmazza a posztokat számozott listaként (`1. cím\n2. cím\n...`), és SHALL JSON tömböt kérjen vissza a releváns sorszámokkal. A system prompt SHALL definiálja a relevancia-kritériumokat (layoff, freeze, anxiety, AI+munka).

#### Scenario: 366 poszt batch triage
- **WHEN** 366 poszt címét küldjük batch triage-ra
- **THEN** egyetlen LLM hívás történik
- **THEN** a válasz JSON tömb releváns sorszámokkal (pl. `[3, 7, 15, ...]`)

### Requirement: Batch triage bővebb szűrés

A batch triage SHALL bővebben szűrjön mint a korábbi keyword filter — a cél hogy ne veszítsünk el releváns posztokat. Inkább legyen false positive (amit a full validation majd kiszűr) mint false negative.

#### Scenario: Implicit freeze jel relevánsként jelölve
- **WHEN** a cím "Az IT fejvadászok hogy nem halnak éhen??"
- **THEN** a poszt relevánsként jelölve (implicit piac-lassulás jel)

#### Scenario: DevOps piaci kérdés relevánsként jelölve
- **WHEN** a cím "DevOps/SRE piac"
- **THEN** a poszt relevánsként jelölve (munkaerőpiaci kérdés)

### Requirement: Batch triage eredmény jelölése

A batch triage után minden poszt SHALL kapjon egy `triage_relevant` boolean mezőt. Csak `triage_relevant=true` posztok mennek tovább a full validation lépésre.

#### Scenario: Releváns poszt jelölése
- **WHEN** a batch triage a poszt sorszámát visszaadja
- **THEN** a poszt `triage_relevant` mezője `true`

#### Scenario: Irreleváns poszt jelölése
- **WHEN** a batch triage NEM adja vissza a poszt sorszámát
- **THEN** a poszt `triage_relevant` mezője `false`
- **THEN** a poszt NEM kerül full validation-re

### Requirement: Batch triage hiba-kezelés

Ha a batch triage LLM hívás sikertelen, a rendszer SHALL fallback-eljen a keyword-alapú `_score_relevance()` szűrésre (`relevance >= 1`).

#### Scenario: LLM hívás sikertelen
- **WHEN** a batch triage API hívás hibát ad (timeout, parse error, HTTP error)
- **THEN** a rendszer kiír egy warning-ot
- **THEN** a keyword-alapú relevance scoring-ot használja szűrőként
- **THEN** `relevance >= 1` posztok mennek tovább full validation-re
