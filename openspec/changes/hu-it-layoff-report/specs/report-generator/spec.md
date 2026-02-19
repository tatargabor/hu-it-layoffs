## ADDED Requirements

### Requirement: Generate timeline section
The report SHALL include a chronological timeline of IT layoff events from 2023 to present, grouped by quarter.

#### Scenario: Quarter grouping
- **WHEN** report generates the timeline
- **THEN** each quarter SHALL show: number of posts, affected companies, estimated total headcount
- **THEN** quarters with no events SHALL still appear with "Nincs adat" marker

### Requirement: Generate company summary table
The report SHALL include a table of all identified companies with columns: Company, Date(s), Estimated Headcount, Source (post link), AI-attributed.

#### Scenario: Company with multiple events
- **WHEN** a company appears in multiple posts (e.g. Ericsson in 2024 and 2025)
- **THEN** each event SHALL be a separate row in the table

#### Scenario: Company with estimated headcount
- **WHEN** headcount is estimated (not explicit)
- **THEN** the number SHALL be prefixed with `~` and shown as a range (e.g. `~50-100`)

### Requirement: Generate aggregate statistics
The report SHALL include:
- Total number of layoff-related posts
- Total number of unique companies affected
- Total estimated people affected (range: min-max across all posts with relevance >= 2)
- Number of posts mentioning AI as a factor
- Number of hiring freeze signals

#### Scenario: Stats calculation
- **WHEN** report generates statistics
- **THEN** it SHALL only count posts with relevance score >= 2
- **THEN** headcount totals SHALL show both min and max ranges

### Requirement: Generate trend analysis
The report SHALL include a textual trend section describing:
- Whether layoff frequency is increasing, stable, or decreasing over time
- Which sectors/company types are most affected (multi vs. startup vs. KKV)
- The role of AI attribution over time (is it increasing?)

#### Scenario: Trend with acceleration
- **WHEN** 2026 Q1 has more events than any previous quarter
- **THEN** trend section SHALL note the acceleration

### Requirement: Generate hiring freeze / open positions section
The report SHALL include a section on hiring signals — posts about difficulty finding work, hiring freezes, and álláspiac romlás.

#### Scenario: Hiring freeze evidence
- **WHEN** posts with `hiring_freeze_signal: true` exist
- **THEN** they SHALL be listed with date, title, and key quote

### Requirement: Output as markdown file
The report SHALL be written to `data/report.md` in valid GitHub-flavored markdown.

#### Scenario: Report structure
- **WHEN** report is generated
- **THEN** it SHALL contain sections in this order: Summary, Timeline, Company Table, Aggregate Stats, Trend Analysis, Hiring Signals, Data Sources
- **THEN** each section SHALL have a level-2 heading (`##`)

### Requirement: Data sources section
The report SHALL end with a list of all Reddit posts used, with links, as a reference section.

#### Scenario: Source listing
- **WHEN** report includes data sources
- **THEN** each source SHALL be a markdown link with date and title
- **THEN** sources SHALL be sorted by date descending
