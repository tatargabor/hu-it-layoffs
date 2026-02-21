## MODIFIED Requirements

### Requirement: Validate posts via GitHub Models API
Az LLM validator SHALL a batch triage által `triage_relevant=true`-nak jelölt posztokat validálja (a korábbi `relevance >= 1` keyword-szűrő helyett). Ha batch triage nem futott (LLM nem elérhető), SHALL fallback-eljen a `relevance >= 1` szűrőre.

#### Scenario: Batch triage utáni validálás
- **WHEN** batch triage sikeresen futott és 120 posztot jelölt relevánsnak
- **THEN** a validator 120 posztot küld az LLM-nek egyenként

#### Scenario: Fallback keyword-szűrőre
- **WHEN** batch triage nem futott (LLM nem elérhető volt a triage fázisban)
- **THEN** a validator a `relevance >= 1` posztokat validálja (régi viselkedés)

### Requirement: Structured prompt with few-shot examples
A validator SHALL bővített SYSTEM_PROMPT-ot használjon amely tartalmazza az `ai_role` mezőt (`direct`, `factor`, `concern`, `none`) és az `ai_context` mezőt (1 mondatos magyarázat ha ai_role nem "none", egyébként null). A few-shot példák SHALL tartalmazzanak AI-attributiós esetet is.

#### Scenario: AI-attributiós few-shot példa
- **WHEN** a SYSTEM_PROMPT tartalmazza a "Szállás Group 70 fejlesztőt bocsát el, AI által megoldott fejlesztések" példát
- **THEN** az elvárt output SHALL tartalmazza `ai_role: "factor"` és `ai_context` magyarázatot

#### Scenario: AI-mentes few-shot példa
- **WHEN** a SYSTEM_PROMPT tartalmazza a "Continental Budapesten leépítés, divízió áthelyezése" példát
- **THEN** az elvárt output SHALL tartalmazza `ai_role: "none"` és `ai_context: null`

### Requirement: Enrich analyzed posts with LLM results
A validator SHALL az eddigi mezők mellett a következő új mezőket is mentse minden validált posztra:
- `llm_ai_role`: str (`direct`, `factor`, `concern`, `none`)
- `llm_ai_context`: str|null (1 mondatos magyarázat ha ai_role nem "none")

#### Scenario: AI factor poszt mentése
- **WHEN** az LLM `ai_role: "factor"`, `ai_context: "Automatizálás csökkentette az igényt"` választ ad
- **THEN** a poszt `llm_ai_role` mezője `"factor"`
- **THEN** a poszt `llm_ai_context` mezője `"Automatizálás csökkentette az igényt"`

## ADDED Requirements

### Requirement: Pipeline támogatja a batch triage integrációt

A `validate_posts()` függvény SHALL elfogadjon egy opcionális `triage_results` paramétert (dict: post_id → bool). Ha megadva, a függvény SHALL ezt használja a posztok szűréséhez a keyword-alapú relevance helyett.

#### Scenario: Triage results paraméter használata
- **WHEN** `validate_posts(posts, triage_results={"abc123": True, "def456": False})`
- **THEN** csak az `abc123` ID-jű poszt kerül LLM validálásra
- **THEN** a `def456` ID-jű poszt `llm_validated=false` marad

#### Scenario: Triage results nélkül (backward compatible)
- **WHEN** `validate_posts(posts)` triage_results nélkül
- **THEN** a régi viselkedés: `relevance >= 1` posztok validálása
