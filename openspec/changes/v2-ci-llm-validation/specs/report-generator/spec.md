## MODIFIED Requirements

### Requirement: Generate aggregate statistics
The report SHALL include:
- Total estimated people affected (range: min-max across all posts with effective relevance >= 2) — **THIS SHALL BE THE FIRST STAT**
- Total number of layoff-related posts
- Total number of unique companies affected
- Number of posts mentioning AI as a factor
- Number of hiring freeze signals

The report SHALL use `llm_relevance` when `llm_validated` is true, otherwise fall back to `relevance`.

#### Scenario: Stats calculation with LLM data
- **WHEN** report generates statistics and posts have `llm_validated: true`
- **THEN** it SHALL use `llm_relevance` for filtering
- **THEN** headcount SHALL use `llm_headcount` when available, falling back to `headcount_min`/`headcount_max`

#### Scenario: Stats calculation without LLM data
- **WHEN** posts have `llm_validated: false`
- **THEN** it SHALL use keyword-based `relevance` for filtering (same as v1)

#### Scenario: Headcount is first stat
- **WHEN** report generates the summary section
- **THEN** the estimated affected headcount SHALL appear before post count and company count

## ADDED Requirements

### Requirement: Generate detailed post table
The report SHALL include a "Detailed Table" section listing ALL posts with relevance >= 1. Columns: Date, Title (linked), Company, Headcount, Category, Score, Comments, Relevance, LLM Confidence, AI-attributed.

#### Scenario: All relevant posts listed
- **WHEN** report generates the detailed table
- **THEN** every post with effective relevance >= 1 SHALL appear
- **THEN** posts SHALL be sorted by date descending

#### Scenario: LLM confidence display
- **WHEN** a post has `llm_validated: true`
- **THEN** the confidence column SHALL show the `llm_confidence` value as percentage
- **WHEN** a post has `llm_validated: false`
- **THEN** the confidence column SHALL show "—"

### Requirement: Generate technologies and roles breakdown
The report SHALL include a section listing the most frequently mentioned programming languages/frameworks and job roles across all LLM-validated posts. Technologies and roles SHALL be aggregated across all posts and shown as ranked lists with occurrence counts.

#### Scenario: Technologies breakdown
- **WHEN** LLM-validated posts contain `llm_technologies` data
- **THEN** the report SHALL list technologies sorted by frequency (e.g. "Java: 12 poszt, React: 8 poszt")

#### Scenario: Roles breakdown
- **WHEN** LLM-validated posts contain `llm_roles` data
- **THEN** the report SHALL list roles sorted by frequency (e.g. "backend fejlesztő: 15 poszt, QA: 7 poszt")

#### Scenario: No LLM data
- **WHEN** no posts have `llm_validated: true`
- **THEN** the technologies and roles section SHALL be omitted

### Requirement: Use effective relevance
The report SHALL define "effective relevance" as: `llm_relevance` if `llm_validated` is true, otherwise `relevance`. All filtering and display throughout the report SHALL use effective relevance.

#### Scenario: Mixed validated and non-validated posts
- **WHEN** some posts are LLM-validated and others are not
- **THEN** each post SHALL use its own effective relevance independently
