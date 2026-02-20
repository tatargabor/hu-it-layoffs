## MODIFIED Requirements

### Requirement: LLM válasz-séma tartalmaz category mezőt

A `SYSTEM_PROMPT` JSON válasz-sémája SHALL tartalmazza a `category` mezőt a következő értékekkel: `layoff`, `freeze`, `anxiety`, `other`. A prompt SHALL definiálja mindegyik kategória jelentését és SHALL tartalmazzon példát minden kategóriára.

#### Scenario: LLM layoff kategóriát ad közvetlen leépítés posztra
- **WHEN** a poszt konkrét IT leépítésről szól (pl. "Ericsson 200 embert bocsát el")
- **THEN** az LLM válasz `category` mezője `layoff` értéket tartalmaz

#### Scenario: LLM freeze kategóriát ad álláspiac-romlás posztra
- **WHEN** a poszt hiring freeze-ről, nehéz elhelyezkedésről, álláspiac-romlásról szól (pl. "Lassan egy éve nem találok munkát")
- **THEN** az LLM válasz `category` mezője `freeze` értéket tartalmaz

#### Scenario: LLM anxiety kategóriát ad karrier-aggodalom posztra
- **WHEN** a poszt karrier-bizonytalanságról, kiégésről, pályaváltásról szól (pl. "Megéri programozónak tanulni?")
- **THEN** az LLM válasz `category` mezője `anxiety` értéket tartalmaz

#### Scenario: LLM other kategóriát ad irreleváns posztra
- **WHEN** a poszt nem kapcsolódik leépítéshez, álláspiachoz vagy karrier-aggodalomhoz
- **THEN** az LLM válasz `category` mezője `other` értéket tartalmaz

### Requirement: Relevancia-mapping kategória-alapú

Az `_map_relevance()` függvény SHALL a `category` mező alapján határozza meg a relevancia-pontszámot. A mapping:
- `layoff` + confidence >= 0.7 → relevance 3
- `layoff` + confidence >= 0.4 → relevance 2
- `freeze` → relevance 2
- `anxiety` → relevance 1
- `other` → relevance 0

#### Scenario: Layoff magas confidence-szel relevance 3 kapjon
- **WHEN** az LLM válasz `category=layoff` és `confidence >= 0.7`
- **THEN** a poszt `llm_relevance` értéke 3

#### Scenario: Freeze poszt relevance 2 kapjon
- **WHEN** az LLM válasz `category=freeze`
- **THEN** a poszt `llm_relevance` értéke 2

#### Scenario: Anxiety poszt relevance 1 kapjon
- **WHEN** az LLM válasz `category=anxiety`
- **THEN** a poszt `llm_relevance` értéke 1

#### Scenario: Other poszt relevance 0 kapjon
- **WHEN** az LLM válasz `category=other`
- **THEN** a poszt `llm_relevance` értéke 0

### Requirement: Backward compatibility régi validált adatokkal

Ha a validált poszt NEM tartalmaz `category` mezőt (régi adat), az `_map_relevance()` SHALL fallback-eljen a jelenlegi `is_actual_layoff` alapú logikára.

#### Scenario: Régi validált poszt category nélkül
- **WHEN** a validált poszt `llm_validated=true` de nincs `category` kulcs az LLM eredményben
- **THEN** a rendszer az `is_actual_layoff` és `confidence` alapján számol relevancia-pontszámot a régi logikával

### Requirement: llm_category mező mentése

A validált posztok SHALL tartalmazzák az `llm_category` mezőt az LLM által visszaadott kategória értékkel.

#### Scenario: Category mező mentése validált posztra
- **WHEN** az LLM sikeresen validál egy posztot és `category=freeze`-t ad
- **THEN** a poszt `llm_category` mezője `freeze` értéket kap
