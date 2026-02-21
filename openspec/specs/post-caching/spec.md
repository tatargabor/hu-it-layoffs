## ADDED Requirements

### Requirement: Frozen posts persistence
The pipeline SHALL maintain a `persisted_data/frozen_posts.json` file containing validated posts older than 60 days. Frozen posts SHALL NOT be re-scraped, re-triaged, or re-validated in subsequent pipeline runs.

#### Scenario: First freeze run
- **WHEN** the pipeline runs and `persisted_data/frozen_posts.json` does not exist
- **THEN** the pipeline SHALL create it and freeze all posts where `llm_validated == True` AND `date < (now - 60 days)` AND `llm_hungarian_relevance` field exists

#### Scenario: Incremental freeze
- **WHEN** the pipeline completes validation and new posts meet the freeze criteria (`llm_validated == True`, `date < now - 60 days`, `llm_hungarian_relevance` exists)
- **THEN** those posts SHALL be appended to `persisted_data/frozen_posts.json`

#### Scenario: Frozen post not re-processed
- **WHEN** the pipeline runs and a post ID exists in `persisted_data/frozen_posts.json`
- **THEN** the pipeline SHALL skip `fetch_post_details`, `batch_triage`, and `validate_posts` for that post

### Requirement: Merged output for report
The pipeline SHALL merge frozen posts with freshly validated posts into `data/validated_posts.json` before report generation. The merged output SHALL be identical in format to the current `validated_posts.json`.

#### Scenario: Report sees all posts
- **WHEN** the report generator runs on merged data
- **THEN** it SHALL contain both frozen (old) and fresh (new) posts, indistinguishable in format

### Requirement: Reddit edited field collection
The scraper SHALL collect the `edited` field from the Reddit API response. The field value SHALL be `false` (never edited) or a Unix timestamp (last edit time).

#### Scenario: Post never edited
- **WHEN** a Reddit post has `edited: false` in the API response
- **THEN** the scraper SHALL save `"edited": false` in the post dict

#### Scenario: Post was edited
- **WHEN** a Reddit post has `edited: 1706123456` in the API response
- **THEN** the scraper SHALL save `"edited": 1706123456` in the post dict

### Requirement: Scrape cutoff for frozen posts
The `fetch_post_details` step SHALL skip posts whose ID exists in the frozen posts set. This avoids fetching comments for posts that will not be re-validated.

#### Scenario: Frozen Reddit post skipped
- **WHEN** `fetch_post_details` encounters a post with ID present in frozen_posts
- **THEN** it SHALL skip the API call and leave the post unchanged
