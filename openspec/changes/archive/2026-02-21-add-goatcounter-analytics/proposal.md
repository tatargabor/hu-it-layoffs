## Why

The report dashboard (GitHub Pages) has zero visitor tracking. We have no idea how many people view the report daily. GoatCounter is a lightweight, cookie-free, GDPR-friendly analytics service — perfect for a single static page.

## What Changes

- Add GoatCounter `<script>` tag to the generated `report.html` (before `</body>`)
- GoatCounter account already created: `hu-it-layoffs.goatcounter.com`
- No cookie consent banner needed (GoatCounter is cookie-free)

## Capabilities

### New Capabilities
- `page-analytics`: GoatCounter script injection into generated HTML

### Modified Capabilities
<!-- None — no existing specs to modify -->

## Impact

- **Code**: `src/visualize.py` — `generate_html()` function, insert script before `</body>`
- **Dependencies**: None (external CDN script loaded by browser)
- **Systems**: GoatCounter dashboard at `hu-it-layoffs.goatcounter.com`
