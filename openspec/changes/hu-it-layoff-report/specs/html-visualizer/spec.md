## ADDED Requirements

### Requirement: Generate interactive HTML dashboard
The visualizer SHALL generate a single self-contained HTML file at `data/report.html` using Chart.js loaded from CDN. No build step or local dependencies required.

#### Scenario: Open in browser
- **WHEN** user opens `data/report.html` in any modern browser
- **THEN** it SHALL render 6 interactive charts and a data table without any server

### Requirement: Display summary statistics
The dashboard SHALL show key metrics at the top: total relevant posts, direct layoff count, affected companies count, estimated headcount range, AI-mentioning posts, hiring freeze signals.

#### Scenario: Stats cards
- **WHEN** dashboard loads
- **THEN** 6 stat cards SHALL be visible with numbers and labels

### Requirement: Quarterly timeline chart
The dashboard SHALL include a stacked bar chart showing posts per quarter (2023 Q1 – present) with three series: direct layoff (relevance 3), strong signal (relevance 2), indirect (relevance 1). A line overlay SHALL show hiring freeze signals per quarter.

#### Scenario: Timeline rendering
- **WHEN** dashboard renders the timeline
- **THEN** bars SHALL be stacked by relevance level
- **THEN** hiring freeze line SHALL overlay on the same y-axis

### Requirement: Headcount estimation chart
The dashboard SHALL include a bar chart showing estimated min/max headcount per quarter.

#### Scenario: Headcount range display
- **WHEN** a quarter has headcount data
- **THEN** two bars (min and max) SHALL be shown side by side

### Requirement: Company bar chart
The dashboard SHALL include a horizontal bar chart showing number of posts per identified company, sorted by count descending.

#### Scenario: Company ranking
- **WHEN** dashboard renders
- **THEN** companies SHALL appear sorted by post count

### Requirement: Sector and category doughnut charts
The dashboard SHALL include two doughnut charts: one for sector distribution (fintech, telecom, etc.) and one for post categories (layoff, freeze, anxiety, other).

#### Scenario: Doughnut rendering
- **WHEN** dashboard renders
- **THEN** both doughnut charts SHALL show labeled segments with counts

### Requirement: AI attribution trend chart
The dashboard SHALL include a bar chart showing AI-mentioning posts vs total relevant posts per year.

#### Scenario: AI trend display
- **WHEN** dashboard renders
- **THEN** each year SHALL show two bars: AI-attributed and total

### Requirement: Top posts table
The dashboard SHALL include a sortable table of top 30 posts (relevance >= 2) with columns: date, title (linked), company, category, score, comments, relevance stars.

#### Scenario: Post table rendering
- **WHEN** dashboard renders
- **THEN** table SHALL show up to 30 posts sorted by date descending
- **THEN** each title SHALL be a clickable link to the Reddit post
