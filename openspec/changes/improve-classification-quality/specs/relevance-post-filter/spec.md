## MODIFIED Requirements

### Requirement: IT sector whitelist (replaces blacklist)

An `_IT_SECTORS_STRICT` set SHALL define auto-pass IT sectors: `fintech`, `big tech`, `IT services`, `telecom`, `startup`. An `_IT_SECTORS_SOFT` set SHALL define IT sectors that require IT keyword evidence: `general IT`, `retail tech`, `gaming tech`, `travel tech`.

Posts with sector in `_IT_SECTORS_STRICT` SHALL auto-pass `_is_it_relevant()`. Posts with sector in `_IT_SECTORS_SOFT` SHALL pass only if IT role/technology keywords are found in `llm_roles`, `llm_technologies`, or `llm_summary`. Posts with any other sector SHALL pass only if IT keywords are found.

This replaces the single `_IT_SECTORS` whitelist that previously included all sectors as auto-pass.

#### Scenario: Government sector layoff without IT roles
- **WHEN** a post has `llm_sector: "government"` and `llm_roles` does not contain IT-related keywords
- **THEN** `_is_it_relevant()` SHALL return False

#### Scenario: Government sector layoff with IT roles
- **WHEN** a post has `llm_sector: "government"` and `llm_roles` contains "informatikus"
- **THEN** `_is_it_relevant()` SHALL return True (e.g. Magyar Posta IT leépítés)

#### Scenario: Retail tech without IT evidence excluded
- **WHEN** a post has `llm_sector: "retail tech"` and no IT keywords in roles/techs/summary (e.g. OBI barkácsáruház)
- **THEN** `_is_it_relevant()` SHALL return False

#### Scenario: Retail tech with IT evidence included
- **WHEN** a post has `llm_sector: "retail tech"` and `llm_roles` contains "fejlesztő" (e.g. Szállás Group)
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: General IT freeze post with IT summary passes
- **WHEN** a post has `llm_sector: "general IT"` and `llm_summary` contains "IT munkát" or "programozó"
- **THEN** `_is_it_relevant()` SHALL return True

#### Scenario: General IT post without any IT keyword fails
- **WHEN** a post has `llm_sector: "general IT"` and no IT keywords in roles/techs/summary
- **THEN** `_is_it_relevant()` SHALL return False
