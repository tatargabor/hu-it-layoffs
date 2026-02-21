## ADDED Requirements

### Requirement: Display project name and tagline
The dashboard header SHALL display "magyar.dev/layoffs" as the project name and "IT Leépítés Radar" as the subtitle. Below this, the tagline "1 óra tervezés, 2 óra generálás" SHALL appear in smaller text.

#### Scenario: Header rendering
- **WHEN** the dashboard loads
- **THEN** "magyar.dev/layoffs" SHALL be the largest text in the header
- **THEN** "IT Leépítés Radar" SHALL appear as a subtitle
- **THEN** "1 óra tervezés, 2 óra generálás" SHALL appear below in smaller, muted text

### Requirement: Display powered-by footer
The dashboard footer SHALL display "powered by Claude Code · OpenSpec · Agentic" in small, muted text alongside the data source attribution.

#### Scenario: Footer content
- **WHEN** user scrolls to the bottom
- **THEN** footer SHALL show "powered by Claude Code · OpenSpec · Agentic"
- **THEN** footer SHALL also show data source info (Reddit publikus API)

### Requirement: Consistent visual identity
The dashboard SHALL use the existing dark theme (#0f0f0f background, #e94560 accent) as the brand palette. The header gradient and accent color SHALL remain consistent.

#### Scenario: Brand colors
- **WHEN** dashboard renders
- **THEN** the accent color (#e94560) SHALL be used for key numbers, highlights, and interactive elements
