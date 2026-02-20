## ADDED Requirements

### Requirement: Methodology section in markdown report
The report generator SHALL include a "Módszertan" section after the main content, describing data collection, analysis pipeline, LLM validation, and limitations.

#### Scenario: Methodology section content
- **WHEN** the markdown report is generated
- **THEN** it SHALL contain a "## Módszertan" section with: adatforrások (subredditek, keresési lekérdezések), elemzési pipeline (keyword scoring → LLM validáció), LLM backend leírás, korlátok, és a GitHub repo link

### Requirement: Methodology section in HTML dashboard
The HTML generator SHALL include an expandable methodology section using `<details>` element.

#### Scenario: Collapsible methodology in dashboard
- **WHEN** the HTML dashboard is generated
- **THEN** it SHALL contain a `<details>` element with the methodology content, collapsed by default

### Requirement: Dashboard link in markdown report
The report generator SHALL include the GitHub Pages dashboard link at the top of the report.

#### Scenario: Dashboard link present
- **WHEN** the markdown report is generated
- **THEN** it SHALL include a link to `https://tatargabor.github.io/hu-it-layoffs/report.html` near the top of the document

### Requirement: Dynamic statistics in methodology
The methodology section SHALL include dynamic statistics from the pipeline run.

#### Scenario: Stats included
- **WHEN** the methodology section is generated with llm_stats available
- **THEN** it SHALL display the number of posts scraped, validated, validation time, and model used
