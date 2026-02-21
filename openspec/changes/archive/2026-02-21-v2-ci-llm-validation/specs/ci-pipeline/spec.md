## ADDED Requirements

### Requirement: Scheduled GitHub Actions workflow
The CI pipeline SHALL run as a GitHub Actions workflow on a cron schedule: twice daily at UTC 06:00 and 18:00 (Hungarian time 07:00 and 19:00). It SHALL also support manual trigger via `workflow_dispatch`.

#### Scenario: Cron trigger
- **WHEN** UTC clock reaches 06:00 or 18:00
- **THEN** the workflow SHALL start automatically

#### Scenario: Manual trigger
- **WHEN** a user clicks "Run workflow" in GitHub Actions UI
- **THEN** the workflow SHALL run the full pipeline

### Requirement: Full pipeline execution
The workflow SHALL execute the pipeline in order: scrape → analyze → LLM validate → generate markdown report → generate HTML report. It SHALL use `python -m src.run` as the entry point.

#### Scenario: Successful pipeline run
- **WHEN** the workflow executes
- **THEN** it SHALL produce updated files in `data/` directory
- **THEN** exit code SHALL be 0

### Requirement: Commit and push data changes
After pipeline execution, the workflow SHALL commit all changes in `data/` and `README.md` to the repository. The commit message SHALL include the run timestamp. The commit SHALL use a bot identity.

#### Scenario: Data changed
- **WHEN** the pipeline produces new or updated files
- **THEN** the workflow SHALL `git add data/ README.md`
- **THEN** the workflow SHALL commit with message "Update report: YYYY-MM-DD HH:MM UTC"
- **THEN** the workflow SHALL push to the current branch

#### Scenario: No data changed
- **WHEN** no files are modified after pipeline run
- **THEN** the workflow SHALL skip the commit step without error

### Requirement: GitHub Pages deployment
The workflow SHALL deploy `data/report.html` to GitHub Pages after each successful run. The Pages source SHALL be configured via GitHub Actions deployment.

#### Scenario: Pages deploy
- **WHEN** a new `data/report.html` is generated
- **THEN** it SHALL be deployed to the GitHub Pages URL for the repository

### Requirement: Concurrency control
The workflow SHALL use a concurrency group to prevent parallel runs. If a new run starts while a previous one is in progress, the previous run SHALL be cancelled.

#### Scenario: Overlapping runs
- **WHEN** a cron trigger fires while a manual run is in progress
- **THEN** the manual run SHALL be cancelled
- **THEN** the cron run SHALL proceed

### Requirement: GITHUB_TOKEN permissions
The workflow SHALL request `contents: write` and `pages: write` permissions for the `GITHUB_TOKEN`. No additional secrets SHALL be required.

#### Scenario: Token permissions
- **WHEN** the workflow runs
- **THEN** it SHALL have write access to push commits
- **THEN** it SHALL have write access to deploy to Pages

### Requirement: README.md generation
The workflow SHALL copy the content of `data/report.md` into `README.md` with an added header linking to the live GitHub Pages dashboard.

#### Scenario: README content
- **WHEN** report is generated
- **THEN** `README.md` SHALL start with a link to the live HTML dashboard
- **THEN** the rest SHALL be the full content of `data/report.md`
