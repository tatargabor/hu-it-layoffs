## ADDED Requirements

### Requirement: Source field on every post
Every post dict SHALL include a `source` field indicating where it came from.

#### Scenario: Reddit post source
- **WHEN** a post comes from Reddit
- **THEN** the `source` field SHALL be `"reddit"` and the existing `subreddit` field provides the specific subreddit

#### Scenario: HUP post source
- **WHEN** a post comes from HUP.hu
- **THEN** the `source` field SHALL be `"hup.hu"` and `subreddit` field SHALL be `"hup.hu"`

### Requirement: Source column in HTML dashboard tables
The HTML dashboard tables (top posts and detailed table) SHALL display a source column.

#### Scenario: Source visible in tables
- **WHEN** viewing the HTML dashboard
- **THEN** each table row SHALL show the source (e.g., "r/programmingHungary", "hup.hu")

### Requirement: Source column in markdown report tables
The markdown report detailed table SHALL include a source column.

#### Scenario: Source in markdown table
- **WHEN** viewing the markdown report
- **THEN** the detailed table and company table SHALL include the post source

### Requirement: Source breakdown in statistics
The dashboard SHALL show a breakdown of posts by source.

#### Scenario: Source distribution chart or summary
- **WHEN** viewing the HTML dashboard
- **THEN** there SHALL be a visible summary showing how many posts come from each source
