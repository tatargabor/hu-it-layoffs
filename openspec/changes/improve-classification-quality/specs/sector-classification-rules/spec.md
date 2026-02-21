## ADDED Requirements

### Requirement: Two-tier IT sector whitelist

The `_IT_SECTORS` set SHALL be split into two tiers:
- **Strict tier** (`_IT_SECTORS_STRICT`): `fintech`, `big tech`, `IT services`, `telecom`, `startup` — these auto-pass `_is_it_relevant()` without IT keyword check.
- **Soft tier** (`_IT_SECTORS_SOFT`): `general IT`, `retail tech`, `gaming tech`, `travel tech` — these pass `_is_it_relevant()` ONLY if IT role/technology keywords are found in `llm_roles`, `llm_technologies`, or `llm_summary`.

All other sectors (automotive, government, entertainment, energy, hospitality, transportation, manufacturing, etc.) SHALL require IT keyword evidence to pass `_is_it_relevant()`.

#### Scenario: Strict tier sector auto-passes
- **WHEN** a post has `llm_sector: "telecom"` and empty `llm_roles` and `llm_technologies`
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: Soft tier sector with IT keyword passes
- **WHEN** a post has `llm_sector: "general IT"` and `llm_summary` contains "fejlesztő"
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: Soft tier sector without IT keyword fails
- **WHEN** a post has `llm_sector: "retail tech"` and `llm_roles: []` and `llm_technologies: []` and `llm_summary` does not contain any IT keyword
- **THEN** `_is_it_relevant()` SHALL return False

#### Scenario: Non-whitelisted sector with IT keyword passes
- **WHEN** a post has `llm_sector: "government"` and `llm_roles` contains "informatikus"
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: Non-whitelisted sector without IT keyword fails
- **WHEN** a post has `llm_sector: "automotive"` and `llm_roles: ["gyári munkás"]` and no IT keywords in summary
- **THEN** `_is_it_relevant()` SHALL return False

### Requirement: IT keyword list for soft tier and non-IT sector check

The IT keyword check SHALL use the existing `_IT_ROLE_KEYWORDS` set (fejlesztő, programozó, informatikus, szoftver, devops, qa, developer, engineer, software, backend, frontend, machine learning, mesterséges intelligencia) and `_IT_ROLE_KEYWORDS_WB` regex (\b(?:ai|ml|IT|data)\b). These SHALL be applied to the concatenation of `llm_roles`, `llm_technologies`, and `llm_summary`.

#### Scenario: AI keyword in summary triggers IT relevance
- **WHEN** a post has `llm_sector: "general IT"` and `llm_summary` contains "AI" as a whole word
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: Short keyword false positive avoided
- **WHEN** a post has `llm_sector: "retail tech"` and `llm_summary` contains "leállításai" (contains "ai" as substring)
- **THEN** `_is_it_relevant()` SHALL return False (word-boundary regex prevents match)

### Requirement: Consistent whitelist between report.py and visualize.py

The `_IT_SECTORS_STRICT`, `_IT_SECTORS_SOFT` sets and `_is_it_relevant()` function SHALL be identical in both `src/report.py` and `src/visualize.py`.

#### Scenario: Both files use same tier definitions
- **WHEN** `_is_it_relevant()` is called in report.py and visualize.py with the same post
- **THEN** both SHALL return the same result
