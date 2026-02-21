## ADDED Requirements

### Requirement: LLM sector mező a validation válasz-sémában

A full validation SYSTEM_PROMPT JSON válasz-sémája SHALL tartalmazza a `sector` mezőt a következő zárt értéklistával:
- `"fintech"` — bank, pénzügyi szolgáltató, fizetési rendszer IT
- `"automotive"` — autógyár, autóipari beszállító, járműtechnológia
- `"telecom"` — telekommunikáció, hálózati infrastruktúra
- `"big tech"` — nagy nemzetközi tech cég (Microsoft, Google, Meta, stb.)
- `"IT services"` — IT outsourcing, IT tanácsadás, rendszerintegrátor
- `"entertainment"` — szórakoztató ipar, média, gaming tech
- `"energy"` — energiaszektor IT, olaj/gáz tech
- `"retail tech"` — kiskereskedelmi tech, e-commerce tech
- `"startup"` — startup, kis tech cég
- `"government"` — állami IT, közigazgatási rendszer
- `"general IT"` — IT szektor, de konkrét szegmens nem azonosítható
- `"other"` — nem-IT szektor vagy nem besorolható
- `null` — a poszt nem ad elég kontextust szektormeghatározáshoz

Az LLM-nek a poszt teljes kontextusából (cím, szöveg, kommentek) SHALL szektort választania, nem csak cégnév alapján.

#### Scenario: Konkrét cég szektora
- **WHEN** a poszt "Ericsson Budapest 200 embert elbocsát"
- **THEN** az LLM válasz `sector` mezője `"telecom"`

#### Scenario: Cégnév nélküli szektor a kontextusból
- **WHEN** a poszt "Banki IT osztályon nagy leépítés, belső fejlesztés megszűnik"
- **THEN** az LLM válasz `sector` mezője `"fintech"`

#### Scenario: Általános IT poszt szektor nélkül
- **WHEN** a poszt "Lassan egy éve nem találok IT munkát, merre tovább?"
- **THEN** az LLM válasz `sector` mezője `"general IT"`

#### Scenario: Nem-IT poszt
- **WHEN** a poszt "Corvinus nyelvtanárok leépítése"
- **THEN** az LLM válasz `sector` mezője `"other"`

#### Scenario: Nem meghatározható
- **WHEN** a poszt "Megéri tanulni programozni?" (nincs szektor-kontextus)
- **THEN** az LLM válasz `sector` mezője `null`

### Requirement: llm_sector mező mentése a validált posztra

A validate_posts() függvény SHALL mentse az LLM sector válaszát `llm_sector` mezőbe a poszt dict-ben.

#### Scenario: Sector mentése
- **WHEN** az LLM `sector="fintech"` választ ad
- **THEN** a poszt `llm_sector` mezője `"fintech"`

#### Scenario: Null sector mentése
- **WHEN** az LLM `sector=null` választ ad
- **THEN** a poszt `llm_sector` mezője `null`

### Requirement: Szektor fallback lánc a riportban

A report generálás és vizualizáció SHALL a következő fallback láncot használja a szektor meghatározásához:
1. `llm_sector` (ha a poszt llm_validated és van llm_sector)
2. `company_sector` (ha az analyzer talált szektort)
3. `"ismeretlen"` (ha egyik sem elérhető)

#### Scenario: LLM sector elsőbbséget kap
- **WHEN** a poszt `llm_sector="fintech"` és `company_sector=null`
- **THEN** a riportban a szektor `"fintech"`

#### Scenario: LLM sector felülírja az analyzer-t
- **WHEN** a poszt `llm_sector="IT services"` és `company_sector="fintech"`
- **THEN** a riportban a szektor `"IT services"` (LLM a teljes kontextust látja)

#### Scenario: Fallback analyzer-re
- **WHEN** a poszt `llm_validated=false` és `company_sector="automotive"`
- **THEN** a riportban a szektor `"automotive"`

#### Scenario: Mindkettő üres
- **WHEN** a poszt `llm_sector=null` és `company_sector=null`
- **THEN** a riportban a szektor `"ismeretlen"`

### Requirement: Vizualizáció szektoros chart frissítés

A `visualize.py` szektoros chart-ja SHALL a szektor fallback láncot használja a `company_sector` közvetlen olvasása helyett.

#### Scenario: Chart adatforrás
- **WHEN** a szektoros chart generálódik
- **THEN** az adatforrás a fallback lánc (llm_sector → company_sector → ismeretlen)

### Requirement: Cég típus statisztika LLM szektor alapján

A "Cég típus" statisztika SHALL az LLM szektort használja a csoportosításhoz:
- `big tech`, `telecom`, `automotive`, `energy` → "Multinacionális/Nagyvállalat"
- `startup` → "Startup/KKV"
- `fintech`, `IT services`, `retail tech`, `entertainment` → "Közepes/vegyes"
- `government` → "Állami"
- `general IT`, `other`, `ismeretlen`, `null` → "Nem besorolható"

#### Scenario: Automotive multinacionális
- **WHEN** a poszt szektora `"automotive"` (fallback lánc alapján)
- **THEN** a cég típus "Multinacionális/Nagyvállalat"

#### Scenario: Startup
- **WHEN** a poszt szektora `"startup"`
- **THEN** a cég típus "Startup/KKV"

### Requirement: Sector nélküli llm_validated posztok újra-validálása

Ha egy poszt `llm_validated=True` de nincs `llm_sector` mezője, a validate_posts() SHALL újra-validálja (ne ugorja át).

#### Scenario: Régi validált poszt sector nélkül
- **WHEN** egy poszt `llm_validated=True` és `llm_sector` mező nem létezik
- **THEN** a validate_posts() újra-validálja a posztot az LLM-mel

#### Scenario: Friss validált poszt sectorral
- **WHEN** egy poszt `llm_validated=True` és `llm_sector="telecom"`
- **THEN** a validate_posts() átugorja (nem validálja újra)
