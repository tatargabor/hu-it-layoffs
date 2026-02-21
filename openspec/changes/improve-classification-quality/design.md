## Context

Reddit user feedback identified ~144 false positive posts in the strong pool (rel>=2). Root causes:
1. `retail tech` in `_IT_SECTORS` whitelist auto-passes non-IT retail (OBI, BestByte, Tesco)
2. LLM classifies physical stores as "retail tech" instead of "other"
3. Automotive factory worker layoffs get rel=3 (Audi gyári munkás, akkugyár)
4. Career advice posts classified as "freeze" instead of "other"
5. Docler/Byborg event labels fragmented (5 variants for same event)

Current validated data: ~553 posts, ~174 in strong pool. After fixes, expect strong pool to drop to ~80-100 (removing non-IT noise).

## Goals / Non-Goals

**Goals:**
- Eliminate non-IT company false positives (OBI, BestByte, Tesco, UPS as "retail tech")
- Reduce automotive factory worker noise (keep only IT/software roles at automotive companies)
- Tighten freeze category to actual job market signals (not career advice / remote work debates)
- Improve event label consistency for multi-source stories
- Remove "powered by Claude Code · OpenSpec" from public footer

**Non-Goals:**
- Changing the relevance scoring algorithm (0-3 scale stays)
- Changing the pool definitions (relevant/strong/direct thresholds stay)
- Adding new data sources or scrapers
- Achieving perfect classification (LLM inherently has some error rate)

## Decisions

### Decision 1: Two-tier IT sector whitelist

**Choice:** Split `_IT_SECTORS` into strict (auto-pass) and soft (needs IT keyword evidence).

**Strict tier** (auto-pass `_is_it_relevant()`):
- `fintech`, `big tech`, `IT services`, `telecom`, `startup`

**Soft tier** (needs IT role/keyword in roles, techs, or summary):
- `general IT`, `retail tech`, `gaming tech`, `travel tech`

**All other sectors** (automotive, government, entertainment, energy, etc.): always need IT keyword evidence.

**Rationale:** `general IT` often contains freeze/anxiety posts with no specific IT role mentioned (e.g. "nehéz elhelyezkedni") — these are legitimate signals. But `retail tech` should not auto-pass because the LLM misclassifies physical retail as "retail tech". Making both soft means retail tech needs evidence, while general IT freeze posts still need some IT keyword in their summary (which most have).

**Alternative considered:** Remove `retail tech` entirely from whitelist. Rejected because legitimate retail tech companies (Szállás Group, hasznaltauto.hu) would need IT keywords in every post.

### Decision 2: Prompt-level fixes over code-level filtering

**Choice:** Fix classification at the source (LLM prompts) rather than adding post-hoc code filters.

Changes to SYSTEM_PROMPT:
- Tighten `retail tech` definition: "CSAK e-commerce platform, webshop, szállásfoglaló tech. NEM: fizikai bolt/áruház (OBI, BestByte, Tesco, Aldi = sector: 'other')"
- Add automotive negative examples: "Audi/Suzuki/Mercedes GYÁRI MUNKÁS leépítés = other. CSAK fejlesztőközpont/szoftvermérnök = layoff"
- Tighten freeze: "Home office vita, karriertanács, remote munka kérdés = 'other', NEM 'freeze'"
- Add event_label consistency instruction

Changes to TRIAGE_SYSTEM_PROMPT:
- Add explicit "NEM releváns" examples for physical retail and factory worker layoffs

**Rationale:** Code filters are a bandaid — the real problem is the LLM assigning wrong sectors/categories. Better to fix the prompt so future runs produce cleaner data. Code-level whitelist change (Decision 1) is a safety net for cases where the LLM still misclassifies.

### Decision 3: Frozen posts re-validation strategy

**Choice:** Clear frozen posts and re-run full pipeline.

**Rationale:** Frozen posts (persisted_data/frozen_posts.json) were validated with old prompts. With new prompt rules, their classifications may be wrong. The safest approach is to clear the frozen cache so all posts get re-validated with new prompts. Cost: ~$2.50, ~90 min — acceptable for a one-time quality improvement.

**Alternative considered:** Manually patch known bad posts in frozen data. Rejected — too error-prone and doesn't fix borderline cases we haven't identified.

### Decision 4: Footer cleanup

**Choice:** Remove "Specifikálva OpenSpec-kel, generálva Claude Code-dal" tagline and "powered by Claude Code · OpenSpec" footer text.

**Rationale:** Feeds the "AI slop" perception. The methodology section already explains the tooling.

## Risks / Trade-offs

- **Strong pool count drops significantly** → Expected and desired. Better to have 80 accurate signals than 174 noisy ones. The stat cards will show lower numbers but more trustworthy data.
- **LLM still misclassifies some edge cases** → Mitigated by two-tier whitelist as safety net. Accept that ~5-10% error rate is inherent to LLM classification.
- **Frozen posts re-run costs ~$2.50** → One-time cost, acceptable.
- **Soft whitelist may filter some legitimate `general IT` freeze posts** → These posts usually mention IT in their summary anyway, so keyword check should pass. Monitor after re-run.
- **Event label deduplication is fuzzy** → Prompt-level improvement is best effort. Perfect dedup would require post-processing with string similarity, which is out of scope for this change.
