## ADDED Requirements

### Requirement: Group posts by event in dashboard tables
The HTML dashboard SHALL group posts with the same `event_label` into collapsible groups in both the Top Posts and Részletes Táblázat tables.

#### Scenario: Event with multiple posts
- **WHEN** multiple posts share the same `event_label` (e.g., "OTP Bank 2026 Q1 leépítés")
- **THEN** the table SHALL show one representative row for the group
- **AND** a badge SHALL indicate the number of sources (e.g., "8 forrás")
- **AND** clicking/expanding SHALL reveal the individual posts as sub-rows

#### Scenario: Event with single post
- **WHEN** an `event_label` has only one post
- **THEN** it SHALL display as a normal row without grouping UI

#### Scenario: Post without event_label
- **WHEN** a post has no `event_label` (null/empty)
- **THEN** it SHALL display as a normal individual row

### Requirement: Representative post selection
For each event group, the dashboard SHALL select the most informative post as the representative.

#### Scenario: Group contains Reddit post
- **WHEN** an event group contains at least one Reddit post
- **THEN** the Reddit post SHALL be selected as representative (it has body text + comments)

#### Scenario: Group contains only Google News posts
- **WHEN** an event group has no Reddit posts
- **THEN** the post with the highest `llm_relevance` SHALL be selected as representative
- **AND** ties SHALL be broken by most recent date

### Requirement: Group posts by event in markdown report
The markdown report company table SHALL show one row per event, with source count indicated.

#### Scenario: Grouped event in markdown
- **WHEN** an event has multiple posts in the company table
- **THEN** one row SHALL appear with "(+N forrás)" in the source column
- **AND** the link SHALL point to the representative post

### Requirement: Reddit cross-reference indicator
For Google News event groups, the dashboard SHALL show a visual indicator when the same event also has a Reddit post, signaling community discussion exists.

#### Scenario: GN event also discussed on Reddit
- **WHEN** a Google News post's event group also contains a Reddit post
- **THEN** a Reddit indicator icon SHALL appear on the representative row
- **AND** it SHALL link to the Reddit post URL

#### Scenario: GN event without Reddit discussion
- **WHEN** a Google News post's event group has no Reddit post
- **THEN** no Reddit indicator SHALL be shown
