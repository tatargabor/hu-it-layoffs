## ADDED Requirements

### Requirement: Hungarian relevance classification
The LLM validator SYSTEM_PROMPT SHALL include a `hungarian_relevance` field in its JSON schema with values `direct`, `indirect`, or `none`, and a `hungarian_context` field with a one-sentence explanation or null.

#### Scenario: Direct Hungarian relevance
- **WHEN** a post describes a layoff at a company operating in Hungary or affecting Hungarian workers (e.g., "OTP leépítés", "Ericsson Budapest fejlesztők")
- **THEN** the LLM SHALL return `hungarian_relevance: "direct"` and `hungarian_context` with explanation

#### Scenario: Indirect Hungarian relevance
- **WHEN** a post describes a global company layoff where the company has known Hungarian presence, or the article mentions potential Hungarian impact (e.g., "Continental globális leépítés, budapesti központ is érintett lehet")
- **THEN** the LLM SHALL return `hungarian_relevance: "indirect"` and `hungarian_context` with explanation

#### Scenario: No Hungarian relevance
- **WHEN** a post describes a layoff with no Hungarian connection (e.g., "Amazon 14 ezer embert küld el USA-ban", "Ubisoft Torontó leépítés", "Dél-Korea AI munkahelyek")
- **THEN** the LLM SHALL return `hungarian_relevance: "none"` and `hungarian_context: null`

### Requirement: Non-IT sector filtering via prompt
The LLM validator SYSTEM_PROMPT SHALL include explicit examples and instructions that non-IT sector layoffs (retail store workers, food industry, textile, agriculture, military) MUST receive `category: "other"` unless IT/tech positions are specifically affected.

#### Scenario: Non-IT retail layoff
- **WHEN** a post describes a retail store employee being fired (e.g., "bolti eladó kirúgás", "áruházlánc leépítés 100 ember")
- **THEN** the LLM SHALL return `category: "other"` and `sector: "other"`

#### Scenario: IT positions at non-IT company
- **WHEN** a post describes IT positions being cut at a non-IT company (e.g., "Magyar Posta 50 informatikust bocsát el")
- **THEN** the LLM SHALL return `category: "layoff"` with appropriate sector (e.g., `government`)

### Requirement: Relevance mapping with Hungarian filter
The `_map_relevance()` function SHALL cap relevance based on `hungarian_relevance`:
- `none` → max relevance 0
- `indirect` → max relevance 2
- `direct` → no cap (existing logic applies)

#### Scenario: Global layoff gets low relevance
- **WHEN** LLM returns `category: "layoff"`, `confidence: 0.95`, `hungarian_relevance: "none"`
- **THEN** `_map_relevance()` SHALL return 0

#### Scenario: Indirect layoff gets capped relevance
- **WHEN** LLM returns `category: "layoff"`, `confidence: 0.9`, `hungarian_relevance: "indirect"`
- **THEN** `_map_relevance()` SHALL return 2 (capped from 3)

#### Scenario: Direct layoff gets full relevance
- **WHEN** LLM returns `category: "layoff"`, `confidence: 0.9`, `hungarian_relevance: "direct"`
- **THEN** `_map_relevance()` SHALL return 3

### Requirement: Triage prompt Hungarian focus
The TRIAGE_SYSTEM_PROMPT SHALL instruct to mark as relevant ONLY posts with Hungarian relevance (direct or indirect) that concern IT/tech positions or IT labor market.

#### Scenario: Global tech news in Hungarian language
- **WHEN** triage receives a Hungarian-language article about Amazon US layoffs with no Hungarian mention
- **THEN** triage SHALL mark it as NOT relevant

#### Scenario: Hungarian IT layoff
- **WHEN** triage receives an article about OTP IT department layoffs
- **THEN** triage SHALL mark it as relevant

### Requirement: Re-validation trigger for new fields
The `validate_posts()` function SHALL re-validate posts that have `llm_validated=True` but lack the `hungarian_relevance` field, to populate the new fields.

#### Scenario: Old validated post without hungarian_relevance
- **WHEN** a post has `llm_validated=True` and no `hungarian_relevance` key
- **THEN** `validate_posts()` SHALL re-validate it (call LLM again)

### Requirement: Report and visualization filtering
The report generator and visualization SHALL filter displayed posts using `hungarian_relevance != "none"` in addition to existing relevance thresholds.

#### Scenario: Non-Hungarian post excluded from report
- **WHEN** generating the report and a post has `hungarian_relevance: "none"` and `llm_relevance: 0`
- **THEN** the post SHALL NOT appear in the layoff statistics, sector charts, or company tables
