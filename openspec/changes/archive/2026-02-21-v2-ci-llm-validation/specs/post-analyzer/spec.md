## MODIFIED Requirements

### Requirement: Output analyzed JSON
The analyzer SHALL save results to `data/analyzed_posts.json` with all original fields plus: `company`, `company_source`, `headcount_min`, `headcount_max`, `headcount_source`, `relevance`, `ai_attributed`, `ai_context`, `hiring_freeze_signal`, `category` (layoff/freeze/anxiety/other), and `llm_validated` (always false at this stage — LLM validation happens in a separate pipeline step).

#### Scenario: Output completeness
- **WHEN** analyzer completes
- **THEN** every post in `data/analyzed_posts.json` SHALL have all analysis fields populated (nullable fields may be null)
- **THEN** every post SHALL have `llm_validated` set to false
