## ADDED Requirements

### Requirement: IT sector whitelist (replaces blacklist)
An `_IT_SECTORS` whitelist SHALL define IT-relevant sectors: `fintech`, `big tech`, `IT services`, `telecom`, `startup`, `general IT`, `retail tech`. Any sector NOT in this whitelist SHALL be treated as non-IT and only pass `_is_it_relevant()` if IT roles/technologies are mentioned.

#### Scenario: Government sector layoff without IT roles
- **WHEN** a post has `llm_sector: "government"` (not in `_IT_SECTORS`) and `llm_roles` does not contain IT-related keywords
- **THEN** `_is_it_relevant()` SHALL return False

#### Scenario: Government sector layoff with IT roles
- **WHEN** a post has `llm_sector: "government"` and `llm_roles` contains "informatikus"
- **THEN** `_is_it_relevant()` SHALL return True (e.g. Magyar Posta IT leépítés)

#### Scenario: Entertainment sector layoff
- **WHEN** a post has `llm_sector: "entertainment"` (not in `_IT_SECTORS`) and no IT roles/techs
- **THEN** `_is_it_relevant()` SHALL return False

#### Scenario: Unknown future sector
- **WHEN** a post has `llm_sector: "agriculture"` (or any other value not in `_IT_SECTORS`)
- **THEN** `_is_it_relevant()` SHALL return False unless IT roles/technologies are mentioned

### Requirement: Category filter for Top Posts table
The Top Posts table (relevancia >= 2) SHALL exclude posts with `category='other'`. Only `layoff`, `freeze`, and `anxiety` categories SHALL appear.

#### Scenario: Career advice post with category other
- **WHEN** a post has `category: "other"` and `relevance: 2` (e.g. "Junior álláskeresés perspektíva")
- **THEN** the post SHALL NOT appear in the Top Posts table

#### Scenario: Layoff post with category layoff
- **WHEN** a post has `category: "layoff"` and `relevance: 2`
- **THEN** the post SHALL appear in the Top Posts table

#### Scenario: Detailed table unaffected
- **WHEN** a post has `category: "other"` and `relevance: 1`
- **THEN** the post SHALL still appear in the Részletes Táblázat (all relevant posts table)

### Requirement: Generic AI article handling (via LLM prompt + category filter)
Generic AI/workforce articles without specific company/event SHALL be handled by the LLM prompt (assigning `relevance: 1`) combined with the `category != 'other'` filter. No separate `_is_specific_event()` function is needed.

#### Scenario: Generic AI doom article
- **WHEN** a post title is "300 millió munkahely szűnik meg az AI miatt" with no company
- **THEN** the LLM SHALL assign `relevance: 1` and/or `category: "other"` → excluded from Top Posts

#### Scenario: Specific AI layoff at company
- **WHEN** a post mentions AI layoffs AND `llm_company: "Docler"`
- **THEN** the LLM SHALL assign `relevance: 2+` and `category: "layoff"` → included in Top Posts

### Requirement: Hungarian relevance strictness
Posts about purely foreign events without Hungarian connection SHALL be filtered.

#### Scenario: Slovak layoffs with no Hungarian tie
- **WHEN** a post is about layoffs in Slovakia with no Hungarian company/office mentioned
- **THEN** the post SHALL NOT appear on the dashboard

#### Scenario: Foreign company with Hungarian office
- **WHEN** a post describes layoffs at Ericsson (which has Hungarian offices)
- **THEN** the post SHALL appear on the dashboard

### Requirement: LLM prompt enhancement for career posts
The LLM validation prompt SHALL include explicit instructions to assign `relevance: 1` to career advice and job-seeking posts that do not describe a specific layoff event.

#### Scenario: Career advice post
- **WHEN** the LLM validates a post like "Junior álláskeresés perspektíva" or "CV tippek"
- **THEN** it SHALL assign `relevance: 1` and `category: "other"`

#### Scenario: Generic AI workforce article
- **WHEN** the LLM validates a generic article like "300 millió munkahely szűnik meg az AI miatt"
- **THEN** it SHALL assign `relevance: 1` unless a specific Hungarian company/event is mentioned

### Requirement: LLM prompt enhancement for non-Hungarian events
The LLM validation prompt SHALL explicitly instruct to set `hungarian_relevance: "none"` for events with no Hungarian connection.

#### Scenario: Global layoff article
- **WHEN** the LLM validates an article about global layoffs (e.g. "16 ezer munkahely szűnik meg a globális cégcsoportnál")
- **THEN** it SHALL set `hungarian_relevance: "none"` unless Hungarian offices/employees are specifically mentioned
