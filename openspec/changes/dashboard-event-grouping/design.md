## Context

The dashboard and report list every post as a separate row, even when multiple posts cover the same event. The `event_label` field (set by LLM validation) already identifies same-event posts — e.g., "OTP Bank 2026 Q1 leépítés" appears 8 times (7 news portals + 1 Reddit post). Currently 11 event groups have duplicates, totaling 34 redundant rows.

The summary statistics already use `_event_groups()` and `_count_events()` for deduplication, but the post tables don't.

## Goals / Non-Goals

**Goals:**
- Group posts by `event_label` in both HTML dashboard tables (Top Posts, Részletes Táblázat)
- Show one representative post per group (prefer Reddit over Google News)
- Make groups expandable/collapsible to reveal individual sources
- Show source count badge on grouped rows
- Apply similar grouping in markdown report company table

**Non-Goals:**
- Changing event_label assignment logic (LLM validation stays the same)
- Modifying the data model or validated_posts.json format
- Changing summary statistics (already correctly deduplicated)

## Decisions

### D1: Representative post selection
**Decision**: For each event group, select the representative by priority: (1) Reddit post (has body + comments), (2) highest relevance score, (3) most recent date.
**Rationale**: Reddit posts have the richest context. If no Reddit post exists, pick the best-scored GN article.

### D2: HTML implementation
**Decision**: Use nested `<details><summary>` HTML elements within table rows. The summary row shows the representative post + badge. The expandable section shows the other sources as sub-rows.
**Rationale**: Native HTML, no JS needed. Already used for "Részletes Táblázat" section. Consistent with existing dashboard patterns.

### D3: Markdown report grouping
**Decision**: In the company table, show one row per event with "(+N forrás)" suffix in the source column. No expandable sections (markdown doesn't support it).
**Rationale**: Markdown is simpler. The link still goes to the representative post. Users can see all sources in the interactive dashboard.

### D4: Posts without event_label
**Decision**: Posts with no `event_label` (150 out of 229) remain as individual rows — no grouping applied.
**Rationale**: No label means the LLM couldn't determine the event. Safe to show individually.

## Risks / Trade-offs

- **[Nested details in tables]** → Some browsers handle `<details>` in `<td>` differently. Mitigation: test in Chrome/Firefox/Safari. Fallback: use JS toggle instead of native `<details>`.
- **[Representative may not be the "best" post]** → Simple heuristic (Reddit > GN, then by relevance). Good enough for 11 groups. Can refine later if needed.
