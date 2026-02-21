## ADDED Requirements

### Requirement: GoatCounter script in generated HTML
The generated `report.html` SHALL include a GoatCounter analytics script tag before the closing `</body>` tag.

#### Scenario: Script present in output
- **WHEN** `generate_html()` produces the HTML output
- **THEN** the output SHALL contain `<script data-goatcounter="https://hu-it-layoffs.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>` before `</body>`

#### Scenario: Script loads asynchronously
- **WHEN** a visitor loads `report.html` in a browser
- **THEN** the GoatCounter script SHALL load with the `async` attribute, not blocking page rendering
