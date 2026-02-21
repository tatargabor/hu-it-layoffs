## 1. Grouping logic

- [x] 1.1 Add `_group_by_event(posts)` helper in visualize.py — groups posts by `event_label`, returns list of (label, representative, other_posts) tuples. Representative selection: Reddit > highest relevance > most recent.
- [x] 1.2 Add same helper in report.py (or share via import)

## 2. HTML dashboard — Top Posts table

- [x] 2.1 Replace flat post list with grouped output in Top Posts table generation
- [x] 2.2 Grouped rows: show representative post with badge "(N forrás)" and collapsible sub-rows using `<details>` within table
- [x] 2.3 Add Reddit cross-reference icon (small Reddit indicator) on GN event rows that also have a Reddit post, linking to the Reddit URL

## 3. HTML dashboard — Részletes Táblázat

- [x] 3.1 Apply same grouping logic to the Részletes Táblázat (detailed_rows generation)
- [x] 3.2 Grouped rows collapsible with individual sources shown on expand

## 4. Markdown report — Company table

- [x] 4.1 Update company table generation in report.py to show one row per event
- [x] 4.2 Add "(+N forrás)" suffix in source column for multi-source events

## 5. CSS and styling

- [x] 5.1 Add CSS for grouped rows: subtle indent for sub-rows, badge styling for source count
- [x] 5.2 Add CSS for Reddit cross-reference icon (small, inline)

## 6. Verify

- [x] 6.1 Re-generate report.html and verify OTP group shows as 1 expandable row instead of 8
- [x] 6.2 Re-generate report.md and verify company table is deduplicated
- [x] 6.3 Verify posts without event_label still show as individual rows
