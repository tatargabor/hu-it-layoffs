## ADDED Requirements

### Requirement: Multi-source text references
All user-facing text in report.py and visualize.py SHALL reference all data sources (Reddit, Google News, HUP.hu) instead of only Reddit.

#### Scenario: Report header source text
- **WHEN** the markdown report header is generated
- **THEN** the source line SHALL read "Forrás: Reddit, Google News, HUP.hu publikus adatok" (not "Reddit publikus adatok")

#### Scenario: HTML dashboard header
- **WHEN** the HTML dashboard header is rendered
- **THEN** the subtitle SHALL reference "Reddit, Google News, HUP.hu publikus adatok" (not "Reddit (r/programmingHungary, r/hungary)")

#### Scenario: Disclaimer text
- **WHEN** the disclaimer is rendered (MD and HTML)
- **THEN** it SHALL say "publikusan elérhető posztok és hírek" (not "publikusan elérhető Reddit posztok")

### Requirement: Methodology multi-source update
The methodology section in both report.py and visualize.py SHALL describe all three data sources and their collection methods.

#### Scenario: Methodology lists all sources
- **WHEN** the methodology section is rendered
- **THEN** it SHALL describe: (1) Reddit subreddit scraping, (2) Google News RSS with `hl=hu&gl=HU`, (3) HUP.hu forum scraping

#### Scenario: Pipeline description updated
- **WHEN** the pipeline steps are listed in methodology
- **THEN** step 1 SHALL say "Multi-source scraping" (not "Reddit JSON API")

### Requirement: MD report concise format
The markdown report SHALL contain only summary sections with links to the HTML dashboard for detailed data. The report SHALL be under 400 lines.

#### Scenario: No Részletes Táblázat in MD
- **WHEN** the markdown report is generated
- **THEN** it SHALL NOT contain the "Részletes Táblázat" section; instead a link to the HTML dashboard SHALL be present

#### Scenario: No Források post list in MD
- **WHEN** the markdown report is generated
- **THEN** it SHALL NOT contain the per-post "Források" list; instead a link to `data/validated_posts.json` SHALL be present

#### Scenario: Érintett Cégek limited to top 20
- **WHEN** the markdown report generates the "Érintett Cégek" table
- **THEN** it SHALL show at most 20 entries, followed by "További N cég → [dashboard link]" if there are more

#### Scenario: Removed sections
- **WHEN** the markdown report is generated
- **THEN** it SHALL NOT contain "Közösségi Engagement", "Hiring Freeze / Álláspiac Jelzések" részletes lista, "Érintett Technológiák", or "Érintett Munkakörök" sections (these remain in the HTML dashboard only)

### Requirement: Dashboard link in MD
The markdown report SHALL include a prominent link to the interactive HTML dashboard at the top and in place of removed sections.

#### Scenario: Top dashboard link
- **WHEN** the markdown report is generated
- **THEN** the first line after the title SHALL contain a link to the interactive dashboard

#### Scenario: Replacement links for removed sections
- **WHEN** a section is removed from the MD report
- **THEN** a short note with dashboard link SHALL appear (e.g., "Részletes adatok: [Interaktív Dashboard](link)")
