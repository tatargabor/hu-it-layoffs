## ADDED Requirements

### Requirement: Anthropic backend selection via environment variable
The LLM validator SHALL support `LLM_BACKEND=anthropic` as a third backend option alongside `github` and `ollama`. When selected, it SHALL use the Anthropic Messages API.

#### Scenario: Anthropic backend selected
- **WHEN** `LLM_BACKEND` is set to `anthropic`
- **THEN** `_resolve_backend()` SHALL return a config with `name: "anthropic"`, `url: "https://api.anthropic.com/v1/messages"`, and `model: "claude-haiku-4-5-20241022"`

#### Scenario: Default backend unchanged
- **WHEN** `LLM_BACKEND` is not set
- **THEN** `_resolve_backend()` SHALL default to `github` (existing behavior)

### Requirement: Anthropic API key resolution
The validator SHALL resolve the Anthropic API key from the `ANTHROPIC_API_KEY` environment variable. If the key is not set, the backend SHALL be marked as unavailable.

#### Scenario: API key present
- **WHEN** `LLM_BACKEND=anthropic` and `ANTHROPIC_API_KEY` is set
- **THEN** the backend SHALL include the key in `x-api-key` header

#### Scenario: API key missing
- **WHEN** `LLM_BACKEND=anthropic` and `ANTHROPIC_API_KEY` is not set
- **THEN** `_check_backend()` SHALL print a warning and return False
- **THEN** LLM validation SHALL be skipped gracefully

### Requirement: Anthropic Messages API request format
The `_call_llm()` function SHALL format requests for the Anthropic API differently from the OpenAI-compatible format. The request body SHALL use `system` as a top-level string parameter (not in the messages array), and `messages` SHALL contain only the user message.

#### Scenario: Request format
- **WHEN** calling the Anthropic API
- **THEN** the request body SHALL include `model`, `max_tokens`, `system` (string), and `messages` (array with one user message)
- **THEN** the `Content-Type` header SHALL be `application/json`
- **THEN** the `x-api-key` header SHALL contain the API key
- **THEN** the `anthropic-version` header SHALL be `2023-06-01`

#### Scenario: JSON mode
- **WHEN** calling the Anthropic API
- **THEN** the system prompt SHALL instruct JSON-only output (Anthropic has no native `response_format` parameter)

### Requirement: Anthropic Messages API response parsing
The `_call_llm()` function SHALL parse Anthropic API responses from the `content[0].text` path (not `choices[0].message.content` used by OpenAI format).

#### Scenario: Successful response parsing
- **WHEN** the Anthropic API returns a successful response
- **THEN** the validator SHALL extract JSON from `response["content"][0]["text"]`
- **THEN** the extracted string SHALL be parsed as JSON

#### Scenario: Response parse error
- **WHEN** the response does not contain valid JSON at the expected path
- **THEN** `_call_llm()` SHALL return None
- **THEN** a parse error message SHALL be printed

### Requirement: Anthropic rate limit handling
The `_call_llm()` function SHALL handle HTTP 429 responses from the Anthropic API with exponential backoff, using the same retry logic as the GitHub Models backend.

#### Scenario: Rate limited
- **WHEN** the Anthropic API returns HTTP 429
- **THEN** the validator SHALL retry with exponential backoff (10s, 20s, 40s, 80s, 160s)
- **THEN** maximum retries SHALL be 5

### Requirement: No delay between Anthropic requests
The Anthropic backend SHALL NOT add artificial delay between requests. The Anthropic API has generous rate limits (Haiku: thousands of RPM) that do not require throttling.

#### Scenario: Request timing
- **WHEN** `LLM_BACKEND=anthropic`
- **THEN** the backend config SHALL have `delay: 0`

### Requirement: Custom model override
The validator SHALL support overriding the default Anthropic model via `LLM_MODEL` environment variable.

#### Scenario: Custom model
- **WHEN** `LLM_BACKEND=anthropic` and `LLM_MODEL=claude-sonnet-4-6-20250514`
- **THEN** the backend SHALL use `claude-sonnet-4-6-20250514` as the model

#### Scenario: Default model
- **WHEN** `LLM_BACKEND=anthropic` and `LLM_MODEL` is not set
- **THEN** the backend SHALL use `claude-haiku-4-5-20241022`
