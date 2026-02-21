## Why

Reddit feedback identified significant false positives in the dashboard: non-IT companies (OBI, BestByte, UPS, Tesco) appearing as IT layoffs, automotive factory worker layoffs counted as IT events, and career advice posts ("Home office hátrafelé sült el") classified as hiring freeze signals. Root cause analysis found 144 suspect posts in the strong pool (rel>=2) with no IT evidence. This undermines dashboard credibility — fixing classification quality is the highest-impact improvement available.

## What Changes

- **LLM prompt tuning**: Tighten sector definitions (retail tech = e-commerce/webshop tech only, not physical stores), add explicit negative examples for automotive factory workers, strengthen freeze/anxiety category boundaries to exclude career advice
- **IT sector whitelist refinement**: Remove `retail tech` from auto-pass `_IT_SECTORS` whitelist, require IT role/keyword evidence for soft sectors
- **Freeze category tightening**: Career advice, remote work debates, work-life balance posts → `other` instead of `freeze`
- **Event label normalization**: Docler/Byborg/Gattyán posts have 5 different event labels for the same events — add fuzzy matching or prompt-level consolidation
- **Footer cleanup**: Remove "powered by Claude Code · OpenSpec" tagline from public dashboard

## Capabilities

### New Capabilities
- `sector-classification-rules`: Rules for how sectors map to IT-relevance, including strict vs soft whitelist tiers and negative examples for common misclassifications

### Modified Capabilities
- `llm-validation`: Tighten SYSTEM_PROMPT sector definitions, freeze/anxiety category boundaries, and add negative examples for non-IT layoffs (OBI, BestByte, Audi factory, akkugyár, kórház, egyetem, operaház)
- `relevance-post-filter`: Refine `_IT_SECTORS` whitelist — split into strict (auto-pass) and soft (needs IT keyword) tiers; remove `retail tech` from auto-pass
- `batch-triage`: Add explicit exclusions to TRIAGE_SYSTEM_PROMPT for physical retail/factory layoffs without IT roles

## Impact

- **src/llm_validator.py**: SYSTEM_PROMPT and TRIAGE_SYSTEM_PROMPT text changes, no structural code changes
- **src/report.py**: `_IT_SECTORS` whitelist split into strict/soft tiers, `_is_it_relevant()` logic update
- **src/visualize.py**: Same `_IT_SECTORS` and `_is_it_relevant()` changes (duplicated from report.py)
- **data/validated_posts.json**: Full pipeline re-run needed (~$2.50, ~90 min) to re-classify all posts with updated prompts
- **persisted_data/frozen_posts.json**: Frozen posts need to be unfrozen/re-validated with new prompts, or manually patched
- **Dashboard footer**: Minor HTML text change in visualize.py
