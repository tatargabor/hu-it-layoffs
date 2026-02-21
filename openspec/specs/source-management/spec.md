## ADDED Requirements

### Requirement: Configurable source enablement
The scraper module SHALL support an `ENABLED_SOURCES` configuration that controls which data sources are active. The default value SHALL be `["reddit"]`. Valid source identifiers are: `reddit`, `google-news`, `hup`.

#### Scenario: Default configuration runs Reddit only
- **WHEN** the pipeline runs with no explicit source configuration
- **THEN** only the Reddit scraper SHALL execute
- **AND** Google News and HUP scrapers SHALL be skipped

#### Scenario: Re-enabling a disabled source
- **WHEN** `ENABLED_SOURCES` is set to `["reddit", "google-news"]`
- **THEN** both Reddit and Google News scrapers SHALL execute
- **AND** HUP scraper SHALL be skipped

#### Scenario: Disabled source produces no new posts
- **WHEN** a source is not in `ENABLED_SOURCES`
- **THEN** the scraper SHALL NOT make any HTTP requests for that source
- **AND** existing posts from that source in validated_posts.json SHALL be preserved

### Requirement: Pipeline logging for skipped sources
The pipeline SHALL log which sources are enabled and which are skipped at the start of each run.

#### Scenario: Log message on pipeline start
- **WHEN** the pipeline starts with `ENABLED_SOURCES = ["reddit"]`
- **THEN** the log SHALL contain a message indicating Reddit is enabled and Google News, HUP are skipped

### Requirement: Documentation reflects active sources
README.md, report.py methodology section, and the HTML dashboard SHALL state that Reddit is the sole active data source. Historical data from other sources SHALL be labeled as such.

#### Scenario: README methodology section
- **WHEN** a user reads the README methodology
- **THEN** it SHALL state Reddit as the active source
- **AND** mention that historical Google News data is preserved but no longer actively collected

#### Scenario: HTML dashboard source description
- **WHEN** a user views the HTML dashboard
- **THEN** the methodology/about section SHALL indicate Reddit as the sole active source

#### Scenario: Markdown report methodology
- **WHEN** the markdown report is generated
- **THEN** the methodology section SHALL describe Reddit as the active source
