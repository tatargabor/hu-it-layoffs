## MODIFIED Requirements

### Requirement: Technologies and roles charts
The dashboard SHALL include two additional charts when LLM-validated data is available:
- A horizontal bar chart of most mentioned technologies/languages (top 15)
- A horizontal bar chart of most mentioned job roles (top 10)

Charts SHALL NOT display Y-axis gridlines (`scales.y.grid.display: false`). All Y-axis labels SHALL be visible (`scales.y.ticks.autoSkip: false`). Chart height SHALL be dynamically calculated based on item count (`items * 28px`, minimum 200px) instead of a fixed max-height.

#### Scenario: Technologies chart rendering
- **WHEN** LLM-validated posts contain `llm_technologies` data
- **THEN** a horizontal bar chart SHALL show technologies ranked by frequency
- **THEN** Y-axis gridlines SHALL NOT be displayed
- **THEN** all technology labels SHALL be visible (no autoSkip)

#### Scenario: Roles chart rendering
- **WHEN** LLM-validated posts contain `llm_roles` data
- **THEN** a horizontal bar chart SHALL show roles ranked by frequency
- **THEN** Y-axis gridlines SHALL NOT be displayed

#### Scenario: No LLM data available
- **WHEN** no posts have `llm_validated: true`
- **THEN** the technologies and roles charts SHALL be hidden

## ADDED Requirements

### Requirement: Company chart top N limit
The company bar chart SHALL display a maximum of 15 companies, sorted by event count descending. All companies remain visible in the detailed table.

#### Scenario: More than 15 companies
- **WHEN** there are 37 companies in the dataset
- **THEN** the company chart SHALL show only the top 15
- **THEN** the remaining 22 companies SHALL still appear in the post tables

### Requirement: Company chart gridline and label fix
The company horizontal bar chart SHALL NOT display Y-axis gridlines. All company labels SHALL be visible (autoSkip disabled). Chart height SHALL be dynamically calculated (`items * 28px`, minimum 200px).

#### Scenario: Company chart label visibility
- **WHEN** the company chart renders with 15 companies
- **THEN** all 15 company names SHALL be visible as Y-axis labels
- **THEN** there SHALL be no gridlines between bars (only bars serve as visual separators)
