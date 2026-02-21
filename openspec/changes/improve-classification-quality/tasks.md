## 1. Anthropic SDK + Prompt Caching

- [x] 1.1 Add `anthropic` to requirements.txt (or pip install)
- [x] 1.2 Refactor `_call_llm()` Anthropic branch in `src/llm_validator.py`: replace `urllib.request` with `anthropic.Anthropic` SDK client, add `cache_control: {"type": "ephemeral"}` on system message for prompt caching
- [x] 1.3 Update `_check_backend()` Anthropic branch to use SDK client ping instead of manual HTTP
- [x] 1.4 Keep urllib-based backends (ollama, github, openai) unchanged

## 2. LLM Prompt Tuning

- [x] 2.1 Update SYSTEM_PROMPT `retail tech` sector definition: add "CSAK e-commerce/webshop/szállásfoglaló tech. NEM: fizikai bolt/áruház (OBI, BestByte, Tesco, Aldi = 'other')" in `src/llm_validator.py`
- [x] 2.2 Update SYSTEM_PROMPT automotive examples: add explicit "GYÁRI MUNKÁS/targoncás/termelési dolgozó = 'other'. CSAK fejlesztőközpont/szoftvermérnök = 'layoff'" negative examples in `src/llm_validator.py`
- [x] 2.3 Update SYSTEM_PROMPT freeze/other category boundary: add "Home office vita, karriertanács, remote munka kérdés, kiégés, karrierszünet = 'other', NEM 'freeze'" with examples in `src/llm_validator.py`
- [x] 2.4 Update SYSTEM_PROMPT event_label consistency: add "Ugyanarról a cégcsoportról (pl. Docler/Byborg/Gattyán) használd a legismertebb nevet, NE hozz létre külön labelt aliasoknak" in `src/llm_validator.py`
- [x] 2.5 Update TRIAGE_SYSTEM_PROMPT: add "NEM releváns" section for physical retail (OBI, BestByte), factory worker layoffs, and non-IT institutions (kórház, egyetem, operaház) in `src/llm_validator.py`

## 3. IT Sector Whitelist Refactor

- [x] 3.1 Split `_IT_SECTORS` into `_IT_SECTORS_STRICT` (fintech, big tech, IT services, telecom, startup) and `_IT_SECTORS_SOFT` (general IT, retail tech, gaming tech, travel tech) in `src/report.py`
- [x] 3.2 Update `_is_it_relevant()` in `src/report.py`: strict auto-passes, soft needs IT keyword check, all other sectors need IT keyword check
- [x] 3.3 Apply identical changes to `src/visualize.py` (`_IT_SECTORS_STRICT`, `_IT_SECTORS_SOFT`, `_is_it_relevant()`)

## 4. Footer Cleanup

- [x] 4.1 Remove "Specifikálva OpenSpec-kel, generálva Claude Code-dal" tagline from header in `src/visualize.py`
- [x] 4.2 Remove "powered by Claude Code · OpenSpec" from footer text in `src/visualize.py`

## 5. Re-validation

- [ ] 5.1 Clear `persisted_data/frozen_posts.json` (reset to empty array) so all posts get re-validated with new prompts — MANUAL: run when ready to spend ~$2.50
- [ ] 5.2 Run full pipeline (`python3 -m src.run`) with `LLM_BACKEND=anthropic` to re-classify all posts — MANUAL: ~90 min runtime
- [ ] 5.3 Verify results: check that OBI, BestByte, Tesco are no longer in strong pool; check "Home office hátrafelé" is category 'other'; check Audi gyári munkás posts are filtered out; check Szállás Group remains in strong pool; verify prompt caching is active (check cache_creation_input_tokens in API response)

## 6. Deploy Approval Gate

- [x] 6.1 Split `pipeline.yml` single job into two jobs: `build` (run pipeline + upload artifact) and `deploy` (commit + push + Pages deploy), where `deploy` needs `build`
- [x] 6.2 Add `environment: production` to the `deploy` job so GitHub Environment protection rules apply
- [x] 6.3 In the `build` job: upload `data/` and `README.md` as artifact after verification step
- [x] 6.4 In the `deploy` job: download artifact, commit, push, and deploy to Pages
- [x] 6.5 Document in README or repo Settings: create "production" environment in GitHub repo settings with "Required reviewers" protection rule (manual step by repo owner) — MANUAL: Go to GitHub repo → Settings → Environments → New: "production" → Add "Required reviewers" → Save

## 7. Version Display

- [x] 7.1 In `src/visualize.py`, read version from `git describe --tags --always` (subprocess) and display it in the dashboard header next to the generation date (e.g. "v0.2.0 | Reddit + Google News publikus adatok | 2025-02-21")
- [x] 7.2 Accept optional `DASHBOARD_VERSION` env var override (for CI or non-git contexts), fall back to `git describe` if not set
- [x] 7.3 In `pipeline.yml` build job, set `DASHBOARD_VERSION` from `git describe --tags --always` and pass to `python -m src.run`
