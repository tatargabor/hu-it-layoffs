## 1. Anthropic Backend — `src/llm_validator.py`

- [x] 1.1 Add `anthropic` branch to `_resolve_backend()`: read `ANTHROPIC_API_KEY` env var, return config with url `https://api.anthropic.com/v1/messages`, model `claude-haiku-4-5-20241022`, headers (`x-api-key`, `anthropic-version: 2023-06-01`, `Content-Type`), delay 0
- [x] 1.2 Add `anthropic` branch to `_check_backend()`: check if `ANTHROPIC_API_KEY` is present, print status message
- [x] 1.3 Add Anthropic request format to `_call_llm()`: body with `model`, `max_tokens`, `system` (top-level string), `messages` (user only); no `response_format` — JSON instruction stays in system prompt
- [x] 1.4 Add Anthropic response parsing to `_call_llm()`: extract JSON from `content[0].text` instead of `choices[0].message.content`
- [x] 1.5 Support `LLM_MODEL` override for anthropic backend (default: `claude-haiku-4-5-20241022`)

## 2. CI Workflow — `.github/workflows/pipeline.yml`

- [x] 2.1 Create `.github/workflows/pipeline.yml` with daily cron (`0 6 * * *`) and `workflow_dispatch` trigger
- [x] 2.2 Add job: checkout, setup-python 3.12, run `python -m src.run` with `LLM_BACKEND=anthropic` and `ANTHROPIC_API_KEY` from secrets
- [x] 2.3 Add git commit+push step: configure bot user, `git add data/ README.md`, commit with `chore: update report YYYY-MM-DD`, push; skip if no changes (`git diff --quiet`)
- [x] 2.4 Add permissions (`contents: write`, `pages: write`, `id-token: write`) and concurrency group with `cancel-in-progress: true`

## 3. Validation

- [ ] 3.1 Test Anthropic backend locally: `LLM_BACKEND=anthropic ANTHROPIC_API_KEY=... python -m src.run` — verify triage + validate both work
- [x] 3.2 Verify existing backends still work: test `LLM_BACKEND=github` and `LLM_BACKEND=ollama` are unchanged
- [ ] 3.3 Add `ANTHROPIC_API_KEY` repo secret in GitHub Settings
