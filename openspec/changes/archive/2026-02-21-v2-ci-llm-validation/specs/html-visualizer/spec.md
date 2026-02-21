## MODIFIED Requirements

### Requirement: Display summary statistics
The dashboard SHALL show key metrics at the top in this order:
1. Estimated affected headcount (largest, highlighted) — **FIRST**
2. Direct layoff count
3. Total relevant posts
4. Affected companies count
5. AI-mentioning posts
6. Hiring freeze signals

The dashboard SHALL use `llm_relevance` when `llm_validated` is true, otherwise fall back to `relevance`.

#### Scenario: Stats cards order
- **WHEN** dashboard loads
- **THEN** the first stat card SHALL show estimated headcount
- **THEN** it SHALL be visually larger or more prominent than other cards

### Requirement: Top posts table
The dashboard SHALL include a table of top 30 posts (effective relevance >= 2) with columns: date, title (linked), company, category, score, comments, relevance stars. Posts with `llm_validated: true` SHALL show an indicator icon or badge.

#### Scenario: Post table with LLM badge
- **WHEN** a post in the table has `llm_validated: true`
- **THEN** it SHALL display a visual indicator (e.g. checkmark) next to the relevance stars

## ADDED Requirements

### Requirement: Detailed post table section
The dashboard SHALL include a collapsible "Detailed Table" section (using HTML `<details>` element) listing ALL posts with effective relevance >= 1. Columns: Date, Title (linked), Company, Headcount, Category, Score, Comments, Relevance, LLM Confidence (%), AI-attributed.

#### Scenario: Collapsed by default
- **WHEN** dashboard loads
- **THEN** the detailed table SHALL be collapsed (not visible)
- **WHEN** user clicks on the section header
- **THEN** the full table SHALL expand

#### Scenario: All relevant posts included
- **WHEN** detailed table is expanded
- **THEN** it SHALL contain every post with effective relevance >= 1
- **THEN** headcount column SHALL show explicit numbers in bold, estimated with `~` prefix in grey

### Requirement: LLM validation confidence overlay
The quarterly timeline chart SHALL visually distinguish between LLM-validated and keyword-only posts. LLM-validated posts SHALL have full opacity bars, keyword-only posts SHALL have reduced opacity (0.5).

#### Scenario: Mixed validation in same quarter
- **WHEN** a quarter has both LLM-validated and keyword-only posts
- **THEN** the bar SHALL show both segments with different opacity levels

### Requirement: Technologies and roles charts
The dashboard SHALL include two additional charts when LLM-validated data is available:
- A horizontal bar chart of most mentioned technologies/languages (top 15)
- A horizontal bar chart of most mentioned job roles (top 10)

#### Scenario: Technologies chart rendering
- **WHEN** LLM-validated posts contain `llm_technologies` data
- **THEN** a horizontal bar chart SHALL show technologies ranked by frequency

#### Scenario: Roles chart rendering
- **WHEN** LLM-validated posts contain `llm_roles` data
- **THEN** a horizontal bar chart SHALL show roles ranked by frequency

#### Scenario: No LLM data available
- **WHEN** no posts have `llm_validated: true`
- **THEN** the technologies and roles charts SHALL be hidden

### Requirement: Use effective relevance throughout
The dashboard SHALL define "effective relevance" as: `llm_relevance` if `llm_validated` is true, otherwise `relevance`. All filtering, counting, and display SHALL use effective relevance.

#### Scenario: Consistent filtering
- **WHEN** dashboard counts "direct layoff" posts
- **THEN** it SHALL count posts where effective relevance == 3
