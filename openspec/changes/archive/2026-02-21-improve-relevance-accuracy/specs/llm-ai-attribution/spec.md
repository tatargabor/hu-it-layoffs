## ADDED Requirements

### Requirement: LLM-alapú AI attribution a full validation válasz-sémában

A full validation SYSTEM_PROMPT JSON válasz-sémája SHALL tartalmazza az `ai_role` mezőt a következő értékekkel:
- `"direct"`: AI/automatizáció közvetlen oka a leépítésnek/változásnak (pl. "AI-val kiváltották a tesztelőket")
- `"factor"`: AI/automatizáció szerepet játszik a háttérben (pl. "automatizálás miatt kevesebb ember kell")
- `"concern"`: AI-val kapcsolatos szorongás/aggodalom (pl. "megéri tanulni, ha AI elveszi a munkát?")
- `"none"`: nincs AI/automatizáció vonatkozás

#### Scenario: Közvetlen AI-alapú leépítés
- **WHEN** a poszt "Az AI-val kiváltották a QA csapat felét a cégnél"
- **THEN** az LLM válasz `ai_role` mezője `"direct"`

#### Scenario: AI mint háttér-faktor
- **WHEN** a poszt "70 fejlesztőt bocsátottak el, az AI által megoldott fejlesztések miatt"
- **THEN** az LLM válasz `ai_role` mezője `"factor"`

#### Scenario: AI-aggodalom
- **WHEN** a poszt "Megéri programozónak tanulni 2025-ben? AI elveszi a munkánkat?"
- **THEN** az LLM válasz `ai_role` mezője `"concern"`

#### Scenario: Nincs AI vonatkozás
- **WHEN** a poszt "Continental Budapesten 50 embert elbocsát, a divízió áthelyezése miatt"
- **THEN** az LLM válasz `ai_role` mezője `"none"`

### Requirement: AI attribution kontextus mentése

Ha `ai_role` nem `"none"`, a validált poszt SHALL kapjon egy `llm_ai_context` mezőt ami az LLM 1 mondatos magyarázata az AI szerepéről.

#### Scenario: AI context mentése
- **WHEN** az LLM `ai_role=factor` és `ai_context="Az automatizálás csökkentette a fejlesztői igényt"` választ ad
- **THEN** a poszt `llm_ai_role` mezője `"factor"`
- **THEN** a poszt `llm_ai_context` mezője `"Az automatizálás csökkentette a fejlesztői igényt"`

#### Scenario: Nincs AI — context üres
- **WHEN** az LLM `ai_role=none` választ ad
- **THEN** a poszt `llm_ai_role` mezője `"none"`
- **THEN** a poszt `llm_ai_context` mezője `null`

### Requirement: LLM AI attribution felülírja keyword-alapút

Ha a poszt LLM-validált, a report SHALL az `llm_ai_role` mezőt használja az `ai_attributed` keyword-alapú mező helyett az AI statisztikákhoz.

#### Scenario: Keyword nem találta de LLM igen
- **WHEN** a poszt `ai_attributed=false` (keyword) de `llm_ai_role="factor"` (LLM)
- **THEN** a report az LLM értéket használja → AI-attributed poszt

#### Scenario: Keyword talált de LLM cáfol
- **WHEN** a poszt `ai_attributed=true` (keyword, hamis pozitív) de `llm_ai_role="none"` (LLM)
- **THEN** a report az LLM értéket használja → NEM AI-attributed
