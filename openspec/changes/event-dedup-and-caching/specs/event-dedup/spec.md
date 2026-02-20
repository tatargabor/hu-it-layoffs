## ADDED Requirements

### Requirement: LLM event_label field
The LLM validator SYSTEM_PROMPT SHALL include an `event_label` field in its JSON schema. The field SHALL contain a normalized event identifier in the format `[Cég] [Helyszín opcionális] [Év QN] [típus]` (e.g., "Audi Győr 2026 Q1 leépítés") or null if the post is not about a specific event.

#### Scenario: Layoff event gets label
- **WHEN** a post describes "Komoly leépítés jön a győri Audi-gyárnál"
- **THEN** the LLM SHALL return `event_label: "Audi Győr 2026 Q1 leépítés"`

#### Scenario: Same event different article gets same label
- **WHEN** a post describes "Leépítés jön a győri Audinál - Portfolio.hu" from the same period
- **THEN** the LLM SHALL return the same `event_label: "Audi Győr 2026 Q1 leépítés"`

#### Scenario: Anxiety post gets null label
- **WHEN** a post is general career anxiety (category=anxiety) without a specific event
- **THEN** the LLM SHALL return `event_label: null`

#### Scenario: Different events at same company get different labels
- **WHEN** Audi has a separate layoff event in Q3 2025 in Germany
- **THEN** the LLM SHALL return `event_label: "Audi Németország 2025 Q3 leépítés"` (different from the Győr event)

### Requirement: Event label field persistence
The `validate_posts()` function SHALL save the `event_label` as `llm_event_label` in the post dict.

#### Scenario: Event label saved
- **WHEN** the LLM returns `event_label: "OTP Bank 2026 Q1 leépítés"`
- **THEN** the post dict SHALL contain `llm_event_label: "OTP Bank 2026 Q1 leépítés"`

### Requirement: Re-validation trigger for event_label
The `validate_posts()` function SHALL re-validate posts that have `llm_validated=True` but lack the `llm_event_label` field.

#### Scenario: Old validated post without event_label
- **WHEN** a post has `llm_validated=True` and no `llm_event_label` key
- **THEN** `validate_posts()` SHALL re-validate it (call LLM again)

### Requirement: Report event-level statistics
The report generator SHALL group posts by `llm_event_label` for aggregate statistics (sector distribution, company counts, timeline). One event = one unit in statistics.

#### Scenario: 11 Audi posts count as 1 event
- **WHEN** generating sector statistics and 11 posts share `llm_event_label: "Audi Győr 2026 Q1 leépítés"`
- **THEN** the automotive sector SHALL count this as 1 event (not 11)

#### Scenario: Posts without event_label counted individually
- **WHEN** a post has `llm_event_label: null` (e.g., general anxiety)
- **THEN** it SHALL be counted as 1 individual unit in statistics

#### Scenario: Detailed table shows all posts
- **WHEN** the detailed post table is rendered
- **THEN** all individual posts SHALL appear (not collapsed by event)

### Requirement: Visualization event-level grouping
The HTML visualization SHALL use event-level grouping for charts (timeline, sector, company) consistent with the report.

#### Scenario: Company chart by events
- **WHEN** rendering the company bar chart
- **THEN** each company's count SHALL reflect unique events (not raw post count)

#### Scenario: Timeline chart by events
- **WHEN** rendering the quarterly timeline
- **THEN** each quarter's count SHALL reflect unique events
