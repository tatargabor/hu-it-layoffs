## 1. Batch Triage

- [x] 1.1 Implement `batch_triage()` function in `src/llm_validator.py` — builds numbered title list, sends single LLM call, parses JSON response with relevant indices
- [x] 1.2 Write batch triage system prompt (Hungarian, IT munkaerőpiac relevancia kritériumok: layoff/freeze/anxiety/AI+munka, bővebb szűrés — inkább false positive mint false negative)
- [x] 1.3 Add fallback logic: if batch triage LLM call fails → fall back to keyword-based `relevance >= 1` filtering
- [x] 1.4 Add `triage_relevant` boolean field to each post based on batch triage results

## 2. LLM AI Attribution

- [x] 2.1 Extend SYSTEM_PROMPT JSON schema with `ai_role` field (direct/factor/concern/none) and `ai_context` field (1 sentence explanation or null)
- [x] 2.2 Add AI attribution few-shot examples to SYSTEM_PROMPT (Szállás Group AI factor, Continental non-AI, career anxiety AI concern)
- [x] 2.3 Save `llm_ai_role` and `llm_ai_context` fields on validated posts in `validate_posts()`

## 3. Pipeline Integration

- [x] 3.1 Modify `validate_posts()` to accept optional `triage_results` parameter (dict: post_id → bool) for filtering instead of `relevance >= 1`
- [x] 3.2 Update `src/run.py` pipeline: analyze → batch_triage → validate_posts(triage_results=...) → report
- [x] 3.3 Update `src/report.py` to use `llm_ai_role` for AI statistics when available (fallback to `ai_attributed` for non-LLM-validated posts)

## 4. Test & Verify

- [x] 4.1 Run full pipeline locally with Ollama and verify batch triage produces ~120+ relevant posts (up from 107 keyword-based)
- [x] 4.2 Verify AI attribution: check that posts like "Szállás Group" and "Continental AI Center" now have correct `llm_ai_role`
- [x] 4.3 Verify fallback: run with LLM_BACKEND=none or unreachable Ollama → keyword filter activates
- [x] 4.4 Regenerate report and verify increased post count and AI attribution stats
