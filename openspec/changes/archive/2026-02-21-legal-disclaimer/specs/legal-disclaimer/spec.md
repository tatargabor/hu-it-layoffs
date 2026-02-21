## ADDED Requirements

### Requirement: Disclaimer in markdown report
The report generator SHALL include a legal disclaimer block after the dashboard link, before the data sections.

#### Scenario: Disclaimer content in MD
- **WHEN** the markdown report is generated
- **THEN** it SHALL contain a disclaimer stating: the content aggregates third-party public Reddit posts, accuracy is not verified, it is for informational/research purposes only, and removal can be requested via GitHub Issues

### Requirement: Disclaimer in HTML dashboard
The HTML generator SHALL include the disclaimer text in the dashboard header area, always visible.

#### Scenario: Disclaimer visible in HTML
- **WHEN** the HTML dashboard is loaded
- **THEN** the disclaimer SHALL be visible below the header, styled as a subtle but readable notice

### Requirement: Bilingual disclaimer
The disclaimer SHALL be written in both Hungarian and English.

#### Scenario: Both languages present
- **WHEN** the disclaimer is displayed
- **THEN** it SHALL contain the Hungarian text first, followed by the English translation

### Requirement: Removal contact
The disclaimer SHALL include a link to request content removal via GitHub Issues.

#### Scenario: Removal link present
- **WHEN** a company or individual wants content removed
- **THEN** the disclaimer SHALL provide a direct link to `https://github.com/tatargabor/hu-it-layoffs/issues`
