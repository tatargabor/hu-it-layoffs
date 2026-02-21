## ADDED Requirements

### Requirement: Social media share buttons
The dashboard SHALL display share buttons for Twitter/X, LinkedIn, Facebook, and Copy Link. Buttons SHALL appear in the header area next to the branding.

#### Scenario: Twitter share
- **WHEN** user clicks the Twitter/X share button
- **THEN** a new tab SHALL open with `https://twitter.com/intent/tweet` pre-filled with the dashboard title and URL

#### Scenario: LinkedIn share
- **WHEN** user clicks the LinkedIn share button
- **THEN** a new tab SHALL open with `https://www.linkedin.com/sharing/share-offsite/` with the dashboard URL

#### Scenario: Facebook share
- **WHEN** user clicks the Facebook share button
- **THEN** a new tab SHALL open with `https://www.facebook.com/sharer/sharer.php` with the dashboard URL

#### Scenario: Copy link
- **WHEN** user clicks the Copy Link button
- **THEN** the dashboard URL SHALL be copied to clipboard via `navigator.clipboard.writeText()`
- **THEN** the button text SHALL change to "Copied!" for 2 seconds

### Requirement: Open Graph meta tags
The HTML SHALL include Open Graph and Twitter Card meta tags for rich link previews when shared on social media.

Required tags:
- `og:title`: "magyar.dev/layoffs — IT Leépítés Radar"
- `og:description`: Dynamic summary with key stats (e.g. "X cég, ~Y-Z érintett, N poszt alapján")
- `og:type`: "website"
- `og:url`: The GitHub Pages URL
- `twitter:card`: "summary"
- `twitter:title`: Same as og:title

#### Scenario: Link preview on Twitter
- **WHEN** someone pastes the dashboard URL on Twitter
- **THEN** the preview SHALL show the title, description, and URL

#### Scenario: Link preview on LinkedIn
- **WHEN** someone shares the dashboard URL on LinkedIn
- **THEN** the preview SHALL show the OG title and description

### Requirement: GitHub Watch button for notifications
The dashboard header SHALL include a "Watch on GitHub" button that links to the repository. Users who Watch the repo will receive email notifications on each report update.

#### Scenario: Watch button click
- **WHEN** user clicks "Watch on GitHub"
- **THEN** a new tab SHALL open with the GitHub repository URL

### Requirement: Section anchor links
Each major section in the dashboard SHALL have an `id` attribute enabling direct linking (e.g. `#timeline`, `#companies`, `#detailed`). Each section header SHALL display a linkable anchor icon on hover.

#### Scenario: Direct link to section
- **WHEN** user visits the dashboard URL with `#companies` hash
- **THEN** the browser SHALL scroll to the companies section

#### Scenario: Copy section link
- **WHEN** user hovers over a section header
- **THEN** a link icon (🔗) SHALL appear
- **WHEN** user clicks the link icon
- **THEN** the URL with the section hash SHALL be copied to clipboard
