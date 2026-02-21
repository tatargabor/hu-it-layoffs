## 1. Ékezet Fix (`src/visualize.py`)

- [x] 1.1 Fix all ékezet-stripped strings in the HTML template (Leepitesek → Leépítések, Kozvetlen → Közvetlen, Negyedeves → Negyedéves, Erintett → Érintett, Becsult → Becsült, etc.)
- [x] 1.2 Fix chart labels and dataset names (Eros jelzes → Erős jelzés, Kozvetett → Közvetett, etc.)
- [x] 1.3 Fix category labels in doughnut chart and table (Karrier aggodalom → Karrier aggodalom is correct, verify all)
- [x] 1.4 Fix footer and all remaining ékezet-stripped text

## 2. Branding (`src/visualize.py`)

- [x] 2.1 Update header: "magyar.dev/layoffs" as main title, "IT Leépítés Radar" as subtitle
- [x] 2.2 Add tagline: "1 óra tervezés, 2 óra generálás" in muted smaller text
- [x] 2.3 Update footer: "powered by Claude Code · OpenSpec · Agentic" alongside data source

## 3. Open Graph Meta Tags (`src/visualize.py`)

- [x] 3.1 Add og:title, og:description (dynamic with stats), og:type, og:url meta tags
- [x] 3.2 Add twitter:card and twitter:title meta tags

## 4. Social Share Buttons (`src/visualize.py`)

- [x] 4.1 Add share buttons row in header: Twitter/X, LinkedIn, Facebook, Copy Link
- [x] 4.2 Implement Twitter share URL (`twitter.com/intent/tweet?text=...&url=...`)
- [x] 4.3 Implement LinkedIn share URL (`linkedin.com/sharing/share-offsite/?url=...`)
- [x] 4.4 Implement Facebook share URL (`facebook.com/sharer/sharer.php?u=...`)
- [x] 4.5 Implement Copy Link with `navigator.clipboard.writeText()` and "Copied!" feedback

## 5. GitHub Watch Button (`src/visualize.py`)

- [x] 5.1 Add "Watch on GitHub" button in header linking to the repository URL

## 6. Section Anchor Links (`src/visualize.py`)

- [x] 6.1 Add `id` attributes to all major sections (timeline, companies, detailed, sources, etc.)
- [x] 6.2 Add hover-visible anchor link icon to section headers with clipboard copy

## 7. Verify

- [x] 7.1 Open report.html in browser — verify all ékezetek are correct
- [x] 7.2 Verify share buttons open correct URLs in new tabs
- [x] 7.3 Verify Copy Link copies to clipboard
- [x] 7.4 Verify section anchor links work (direct URL + hover icon)
- [x] 7.5 Verify OG meta tags with a link preview tool
