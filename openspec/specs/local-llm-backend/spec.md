## ADDED Requirements

### Requirement: Ollama backend support
The system SHALL support Ollama as an alternative LLM backend via its OpenAI-compatible API at `http://localhost:11434/v1/chat/completions`.

#### Scenario: Successful validation with Ollama
- **WHEN** `LLM_BACKEND=ollama` is set and Ollama is running locally
- **THEN** the validator SHALL send requests to `http://localhost:11434/v1/chat/completions` without Authorization header and return the same JSON output structure as the GitHub backend

#### Scenario: Ollama not running
- **WHEN** `LLM_BACKEND=ollama` is set but Ollama is not running
- **THEN** the validator SHALL print "Ollama not reachable at localhost:11434" and skip LLM validation (falling back to keyword scoring)

### Requirement: Backend selection via environment variable
The system SHALL select the LLM backend based on the `LLM_BACKEND` environment variable.

#### Scenario: Default backend
- **WHEN** `LLM_BACKEND` is not set
- **THEN** the system SHALL use the `github` backend (GitHub Models API)

#### Scenario: Ollama backend selected
- **WHEN** `LLM_BACKEND=ollama` is set
- **THEN** the system SHALL use the Ollama backend

### Requirement: Model selection via environment variable
The system SHALL allow model selection via the `LLM_MODEL` environment variable.

#### Scenario: Default model for GitHub backend
- **WHEN** `LLM_BACKEND=github` and `LLM_MODEL` is not set
- **THEN** the system SHALL use `gpt-4o-mini`

#### Scenario: Default model for Ollama backend
- **WHEN** `LLM_BACKEND=ollama` and `LLM_MODEL` is not set
- **THEN** the system SHALL use `llama3.1`

#### Scenario: Custom model
- **WHEN** `LLM_MODEL=mistral` is set
- **THEN** the system SHALL use `mistral` regardless of backend

### Requirement: No rate limiting for local backend
The system SHALL NOT apply request delay between API calls when using the Ollama backend.

#### Scenario: Local backend request timing
- **WHEN** `LLM_BACKEND=ollama` and multiple posts are validated
- **THEN** the system SHALL send requests without any `time.sleep()` delay between them

#### Scenario: GitHub backend retains delay
- **WHEN** `LLM_BACKEND=github` and multiple posts are validated
- **THEN** the system SHALL retain the existing `REQUEST_DELAY` between requests

### Requirement: Same prompt and output format
The system SHALL use the same system prompt and expect the same JSON output schema regardless of which backend is used.

#### Scenario: Output parity
- **WHEN** a post is validated with Ollama backend
- **THEN** the output fields (`llm_validated`, `llm_relevance`, `llm_company`, `llm_confidence`, `llm_summary`, `llm_technologies`, `llm_roles`) SHALL be identical in structure to GitHub backend output
