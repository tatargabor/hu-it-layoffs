## ADDED Requirements

### Requirement: Validate posts via GitHub Models API
The LLM validator SHALL send each analyzed post (relevance >= 1) to the GitHub Models API (gpt-4o-mini) for validation. The request SHALL use the `models.inference.ai.azure.com/chat/completions` endpoint with `response_format: {"type": "json_object"}`.

#### Scenario: Successful validation
- **WHEN** a post with relevance >= 1 is submitted to the LLM
- **THEN** the response SHALL contain: `is_actual_layoff` (bool), `confidence` (0.0-1.0), `company` (str|null), `headcount` (int|null), `summary` (str, 1 sentence Hungarian), `technologies` (list[str], programming languages/frameworks/tools mentioned), `roles` (list[str], job roles/positions mentioned)

#### Scenario: Post with relevance 0 skipped
- **WHEN** a post has relevance 0
- **THEN** the validator SHALL skip it and set `llm_validated` to false

### Requirement: Token resolution chain
The validator SHALL resolve the API token using a 3-step chain:
1. `GITHUB_TOKEN` environment variable
2. `gh auth token` subprocess call (fallback for local dev)
3. None — skip LLM validation entirely (graceful degradation)

#### Scenario: CI environment
- **WHEN** `GITHUB_TOKEN` env var is set
- **THEN** validator SHALL use it directly without subprocess calls

#### Scenario: Local development with gh CLI
- **WHEN** `GITHUB_TOKEN` is not set but `gh` CLI is installed and authenticated
- **THEN** validator SHALL obtain token via `gh auth token`

#### Scenario: No token available
- **WHEN** neither env var nor gh CLI provides a token
- **THEN** validator SHALL print a warning and return posts unchanged
- **THEN** all posts SHALL have `llm_validated` set to false

### Requirement: Structured prompt with few-shot examples
The validator SHALL use a system prompt that includes:
- Task description in Hungarian (IT leépítés validáció)
- JSON output schema definition
- At least 2 few-shot examples (one true positive, one false positive)
- Instruction to respond in Hungarian for the summary field

#### Scenario: True positive example
- **WHEN** prompt includes example of "Ericsson 200 embert bocsát el"
- **THEN** expected output SHALL show `is_actual_layoff: true, confidence: 0.95`

#### Scenario: False positive example
- **WHEN** prompt includes example of "Megéri programozónak tanulni?"
- **THEN** expected output SHALL show `is_actual_layoff: false, confidence: 0.9`

### Requirement: Enrich analyzed posts with LLM results
The validator SHALL add/override these fields on each validated post:
- `llm_validated`: true
- `llm_relevance`: 0-3 (mapped from LLM confidence + is_actual_layoff)
- `llm_company`: str|null (LLM's company identification)
- `llm_headcount`: int|null (LLM's headcount extraction)
- `llm_confidence`: 0.0-1.0
- `llm_summary`: str (1 sentence summary)
- `llm_technologies`: list[str] (programming languages, frameworks, tools mentioned in the post, e.g. ["Java", "React", "SAP", "Kubernetes"])
- `llm_roles`: list[str] (job roles/positions mentioned, e.g. ["backend fejlesztő", "DevOps", "QA engineer", "project manager"])

Mapping: if `is_actual_layoff` is true and confidence >= 0.8 → relevance 3; true and confidence >= 0.5 → relevance 2; false but confidence < 0.7 → relevance 1; false and confidence >= 0.7 → relevance 0.

#### Scenario: High confidence layoff
- **WHEN** LLM returns `is_actual_layoff: true, confidence: 0.92`
- **THEN** `llm_relevance` SHALL be 3

#### Scenario: Uncertain post
- **WHEN** LLM returns `is_actual_layoff: false, confidence: 0.55`
- **THEN** `llm_relevance` SHALL be 1

### Requirement: Rate limiting between requests
The validator SHALL wait at least 0.5 seconds between API requests to stay within GitHub Models free tier limits (150 RPM).

#### Scenario: Sequential processing
- **WHEN** processing 200 posts
- **THEN** total API time SHALL be at least 100 seconds (200 * 0.5s)
- **THEN** no HTTP 429 errors SHALL occur under normal conditions

### Requirement: Output validated JSON
The validator SHALL write results to `data/validated_posts.json` with the same structure as `analyzed_posts.json` plus the LLM fields. If LLM validation was skipped, it SHALL copy `analyzed_posts.json` as-is with `llm_validated: false` on all posts.

#### Scenario: Full validation output
- **WHEN** LLM validation completes successfully
- **THEN** `data/validated_posts.json` SHALL contain all posts with LLM fields

#### Scenario: Skipped validation output
- **WHEN** no token is available
- **THEN** `data/validated_posts.json` SHALL be identical to `analyzed_posts.json` except each post SHALL have `llm_validated: false`

### Requirement: Error handling per post
The validator SHALL handle API errors per-post without aborting the batch. If a single post fails (timeout, malformed response, API error), that post SHALL retain its original keyword-based scoring with `llm_validated: false`.

#### Scenario: Single post API failure
- **WHEN** the API returns an error for one post
- **THEN** that post SHALL keep its original analysis fields
- **THEN** processing SHALL continue with the next post
- **THEN** a warning SHALL be printed with the post ID
