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

On mobile (<=768px), the stats grid SHALL use `grid-template-columns: repeat(2, 1fr)` and the primary stat SHALL span full width with `grid-column: 1 / -1`.

#### Scenario: Stats cards order
- **WHEN** dashboard loads
- **THEN** the first stat card SHALL show estimated headcount
- **THEN** it SHALL be visually larger or more prominent than other cards

#### Scenario: Mobile stats layout
- **WHEN** viewport width is <= 768px
- **THEN** stat cards SHALL display in a 2-column grid
- **THEN** the primary stat card SHALL span both columns

### Requirement: Top posts table
The dashboard SHALL include a table of top 30 posts (effective relevance >= 2) with columns: date, title (linked), company, category, score, comments, relevance stars. Posts with `llm_validated: true` SHALL show an indicator icon or badge.

On mobile, the table SHALL be wrapped in a horizontally scrollable container.

#### Scenario: Post table with LLM badge
- **WHEN** a post in the table has `llm_validated: true`
- **THEN** it SHALL display a visual indicator (e.g. checkmark) next to the relevance stars

#### Scenario: Table horizontal scroll on mobile
- **WHEN** the viewport width is <= 768px and the table is wider than the viewport
- **THEN** the table SHALL scroll horizontally within its container
