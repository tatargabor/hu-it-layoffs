## 1. LLM Validator (`src/llm_validator.py`)

- [x] 1.1 Implement token resolution chain (env var → `gh auth token` → None)
- [x] 1.2 Implement GitHub Models API client (urllib, JSON request/response, `models.inference.ai.azure.com`)
- [x] 1.3 Create structured prompt with few-shot examples (Hungarian IT layoff validation, JSON output schema)
- [x] 1.4 Implement batch validation loop — iterate relevance >= 1 posts, 0.5s delay, per-post error handling
- [x] 1.5 Implement LLM response → post enrichment mapping (llm_validated, llm_relevance, llm_company, llm_headcount, llm_confidence, llm_summary, llm_technologies, llm_roles)
- [x] 1.6 Write `data/validated_posts.json` output (or copy analyzed_posts.json with llm_validated=false on skip)

## 2. Pipeline Integration (`src/run.py`)

- [x] 2.1 Add LLM validation step between analyzer and report (step 3/5)
- [x] 2.2 Add `visualize.py` call to pipeline (step 5/5)
- [x] 2.3 Report and visualizer read `validated_posts.json` instead of `analyzed_posts.json`
- [x] 2.4 Add README.md generation (copy report.md with Pages link header)

## 3. Post Analyzer Update (`src/analyzer.py`)

- [x] 3.1 Add `llm_validated: false` field to all output posts

## 4. Report Generator Update (`src/report.py`)

- [x] 4.1 Implement effective relevance helper (llm_relevance if validated, else relevance)
- [x] 4.2 Reorder summary section — headcount first, then posts/companies/AI/freeze
- [x] 4.3 Use llm_headcount when available for headcount display
- [x] 4.4 Add detailed post table section (all posts relevance >= 1, all columns including LLM confidence)
- [x] 4.5 Add technologies and roles breakdown section (aggregated from llm_technologies/llm_roles, sorted by frequency)

## 5. HTML Visualizer Update (`src/visualize.py`)

- [x] 5.1 Reorder stat cards — headcount first and visually larger
- [x] 5.2 Implement effective relevance throughout all charts and counts
- [x] 5.3 Add LLM validated badge/indicator to top posts table
- [x] 5.4 Add collapsible detailed table (`<details>`) with all posts, headcount bold/grey styling
- [x] 5.5 Add LLM confidence opacity overlay to timeline chart bars
- [x] 5.6 Add technologies horizontal bar chart (top 15, from llm_technologies)
- [x] 5.7 Add roles horizontal bar chart (top 10, from llm_roles)
- [x] 5.8 Hide tech/roles charts when no LLM data available

## 6. GitHub Actions CI (`.github/workflows/report.yml`)

- [x] 6.1 Create workflow file with cron schedule (0 6,18 * * *) and workflow_dispatch trigger
- [x] 6.2 Configure permissions (contents: write, pages: write) and concurrency group
- [x] 6.3 Add pipeline execution step (python -m src.run)
- [x] 6.4 Add git commit & push step (data/ + README.md, skip if no changes)
- [x] 6.5 Add GitHub Pages deployment step (data/report.html)

## 7. Test & Verify

- [x] 7.1 Run full pipeline locally with `gh auth token` — verify LLM validation works
- [x] 7.2 Run full pipeline without token — verify graceful degradation
- [x] 7.3 Review report.md layout (headcount first, detailed table present)
- [x] 7.4 Review report.html (stat order, collapsible table, LLM badges, opacity overlay)
