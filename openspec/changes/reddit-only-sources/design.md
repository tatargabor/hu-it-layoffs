## Context

The pipeline currently scrapes 3 sources: Reddit (4 subreddits), HUP.hu forum, Google News RSS. Analysis of validated_posts.json shows:
- Google News: 449 posts, but 0 body text, 0 comments — title-only validation. Massive duplication (same event 5-10x from different portals). ~80% non-IT sector noise.
- HUP.hu: 0 posts in the dataset — effectively dead source.
- Reddit: 366 posts, 98% have body text, 82% have comments — deep contextual analysis possible.

Google News doubles LLM validation cost (287 extra calls) without proportional value, since the LLM can only work from titles.

## Goals / Non-Goals

**Goals:**
- Disable Google News and HUP.hu scrapers via configuration flag (not code deletion)
- Pipeline runs Reddit-only by default
- Documentation (README, dashboard, report) reflects Reddit as the sole active source
- Existing Google News posts preserved in validated_posts.json as historical data

**Non-Goals:**
- Deleting Google News / HUP scraper code (keep for potential future re-enable)
- Removing historical Google News posts from data files
- Adding new Reddit subreddits or changing Reddit scraper behavior
- Changing LLM validation logic

## Decisions

### D1: Flag-based disable vs code deletion
**Decision**: Add `ENABLED_SOURCES` config in `scraper.py` defaulting to `["reddit"]`. HUP and Google News code stays intact.
**Rationale**: Low-effort to re-enable if Google News later provides article body text (e.g., via direct scraping). Deleting code is irreversible effort for no gain.
**Alternative considered**: Full removal of HUP/GN code — rejected because the code is tested and may be useful later.

### D2: Historical data handling
**Decision**: Keep existing Google News posts in validated_posts.json. They retain their `source: "google-news"` field and appear in reports as historical entries.
**Rationale**: Removing them would lose ~74 unique events. The dashboard already handles mixed sources. No extra cost to keep them.

### D3: Documentation updates
**Decision**: Update README methodology, report.py methodology text, and visualize.py dashboard description to state Reddit is the sole active source, mentioning Google News as historical-only.
**Rationale**: Users need to know the current methodology. Historical data should be explained, not hidden.

## Risks / Trade-offs

- **[Missing IT events only covered by news portals]** → Acceptable: the few IT-relevant GN events (Bitdefender, T-Systems, Nokia) are large enough to eventually appear on Reddit. Monitor for gaps.
- **[Stale flag if someone doesn't know about ENABLED_SOURCES]** → Mitigated by documenting in scraper.py docstring and README.
- **[Historical GN posts may confuse dashboard users]** → Mitigated by clear "historical data" labeling in methodology section.
