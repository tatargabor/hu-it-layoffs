## ADDED Requirements

### Requirement: Identify affected company from post
The analyzer SHALL extract the company name from each post's title, selftext, and comments. It SHALL maintain a known-companies list (OTP, Ericsson, NNG, Microsoft, Continental, Docler/Byborg, Szállás Group, Lensa, SEON, Unisys, CATL, Audi, MNB, Tesco Technology) and also detect new company names from context. Short company keys (<=4 chars) SHALL use regex word boundary matching (`\b`) to avoid false positives (e.g. "mol" matching inside other words).

#### Scenario: Known company in title
- **WHEN** a post title contains "OTP bank - leépítés IT területen"
- **THEN** analyzer SHALL set `company` to "OTP Bank"

#### Scenario: Company mentioned only in comments
- **WHEN** no company is in the title but comments mention a specific company
- **THEN** analyzer SHALL set `company` to that company name
- **THEN** analyzer SHALL set `company_source` to "comment"

#### Scenario: No company identifiable
- **WHEN** no company can be identified from title, selftext, or comments
- **THEN** analyzer SHALL set `company` to `null` and `company_source` to "none"

### Requirement: Estimate affected headcount
The analyzer SHALL extract or estimate the number of affected employees per post.

Rules for estimation:
- If the post contains an explicit number, use it and set `headcount_source` to "explicit"
- If the post says "nagy leépítés" at a known multi (>1000 employees), estimate 50-200 and set `headcount_source` to "estimated"
- If it's a startup/KKV context, estimate 10-30
- If no estimation is possible, set `headcount_min` and `headcount_max` to `null`

#### Scenario: Explicit number in text
- **WHEN** post contains "kb 150 embert érint"
- **THEN** analyzer SHALL set `headcount_min` to 150, `headcount_max` to 150, `headcount_source` to "explicit"

#### Scenario: Estimated from context
- **WHEN** post discusses layoff at a large multinational without specific numbers
- **THEN** analyzer SHALL set `headcount_min` and `headcount_max` as a range
- **THEN** `headcount_source` SHALL be "estimated"

### Requirement: Classify post relevance
The analyzer SHALL assign a relevance score (0-3) to each post:
- **3**: Direct layoff report (specific company, IT sector)
- **2**: Strong signal (álláspiac romlás, hiring freeze, bújtatott leépítés)
- **1**: Indirect signal (career anxiety, "megéri tanulni?", job search struggles)
- **0**: Not relevant (false positive from search)

#### Scenario: Direct layoff report
- **WHEN** post title contains company name AND layoff keyword (leépítés, elbocsátás, layoff)
- **THEN** relevance SHALL be 3

#### Scenario: False positive filtered
- **WHEN** post matches keyword but is about a non-IT topic (e.g. politics, factory)
- **THEN** relevance SHALL be 0

### Requirement: Detect AI attribution
The analyzer SHALL use a two-tier keyword system to flag whether the layoff/situation is attributed to AI. Field: `ai_attributed` (boolean), `ai_context` (relevant quote if true).

**Tier 1 — Strong keywords** (sufficient on their own):
- `ai elveszi a munkát`, `ai miatt leépít`, `ai helyettesít`, `mesterséges intelligencia elveszi`

**Tier 2 — Context keywords** (must co-occur with job/layoff terms in the same post):
- `mesterséges intelligencia`, `chatgpt`, `copilot`, `claude`, `llm`, `machine learning`, `automatizál`
- Job terms for co-occurrence: `munka`, `állás`, `leépít`, `elbocsát`, `fejlesztő`, `programozó`, `elveszi`

Short keywords (<=3 chars) SHALL use regex word boundary matching (`\b`) to avoid false positives.

#### Scenario: Strong AI keyword
- **WHEN** post contains "ai elveszi a munkát"
- **THEN** `ai_attributed` SHALL be true regardless of other content

#### Scenario: Context AI keyword with job terms
- **WHEN** post mentions "chatgpt" AND also contains "fejlesztő" or similar job term
- **THEN** `ai_attributed` SHALL be true

#### Scenario: AI keyword without job context
- **WHEN** post mentions "chatgpt" but discusses coding tools without layoff/job context
- **THEN** `ai_attributed` SHALL be false

### Requirement: Detect hiring freeze signals
The analyzer SHALL identify posts that indicate hiring freezes or lack of open positions. Field: `hiring_freeze_signal` (boolean).

#### Scenario: Hiring freeze mentioned
- **WHEN** post discusses "nincs felvétel", "freeze", "nem vesznek fel", "álláspiac beszűkült"
- **THEN** `hiring_freeze_signal` SHALL be true

### Requirement: Output analyzed JSON
The analyzer SHALL save results to `data/analyzed_posts.json` with all original fields plus: `company`, `company_source`, `headcount_min`, `headcount_max`, `headcount_source`, `relevance`, `ai_attributed`, `ai_context`, `hiring_freeze_signal`, `category` (layoff/freeze/anxiety/other).

#### Scenario: Output completeness
- **WHEN** analyzer completes
- **THEN** every post in `data/analyzed_posts.json` SHALL have all analysis fields populated (nullable fields may be null)
