## MODIFIED Requirements

### Requirement: Generate interactive HTML dashboard
The visualizer SHALL generate a single self-contained HTML file at `data/report.html` using Chart.js loaded from CDN. No build step or local dependencies required. All Hungarian text in the dashboard SHALL use correct ékezetek (á, é, í, ó, ö, ő, ú, ü, ű) — no ASCII substitutions.

#### Scenario: Correct Hungarian characters
- **WHEN** the dashboard renders
- **THEN** all text SHALL use proper Hungarian characters
- **THEN** "Leépítések" SHALL appear instead of "Leepitesek"
- **THEN** "Közvetlen" SHALL appear instead of "Kozvetlen"
- **THEN** "Negyedéves" SHALL appear instead of "Negyedeves"
- **THEN** all other ékezet-stripped text SHALL be corrected

#### Scenario: Open in browser
- **WHEN** user opens `data/report.html` in any modern browser
- **THEN** it SHALL render charts, tables, branding, and share buttons without any server
