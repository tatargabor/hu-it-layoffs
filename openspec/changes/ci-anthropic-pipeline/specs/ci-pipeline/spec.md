## ADDED Requirements

### Requirement: Daily scheduled GitHub Actions workflow
The CI pipeline SHALL run as a GitHub Actions workflow on a daily cron schedule at UTC 06:00 (Hungarian time 07:00). It SHALL also support manual trigger via `workflow_dispatch`.

#### Scenario: Cron trigger
- **WHEN** UTC clock reaches 06:00
- **THEN** the workflow SHALL start automatically

#### Scenario: Manual trigger
- **WHEN** a user clicks "Run workflow" in GitHub Actions UI
- **THEN** the workflow SHALL run the full pipeline

### Requirement: Python environment setup
The workflow SHALL set up Python 3.12 and install no external dependencies. The project uses only stdlib modules (`urllib`, `json`, `os`, `time`, `subprocess`).

#### Scenario: Environment ready
- **WHEN** the workflow starts
- **THEN** it SHALL use `actions/setup-python@v5` with `python-version: "3.12"`
- **THEN** no `pip install` step SHALL be required

### Requirement: Full pipeline execution with Anthropic backend
The workflow SHALL execute `python -m src.run` with environment variables configured for the Anthropic backend.

#### Scenario: Pipeline environment
- **WHEN** the pipeline step runs
- **THEN** `LLM_BACKEND` SHALL be set to `anthropic`
- **THEN** `ANTHROPIC_API_KEY` SHALL be set from `${{ secrets.ANTHROPIC_API_KEY }}`

#### Scenario: Successful pipeline run
- **WHEN** the pipeline completes successfully
- **THEN** it SHALL produce updated files in `data/` directory and `README.md`
- **THEN** exit code SHALL be 0

### Requirement: Commit and push data changes
After pipeline execution, the workflow SHALL commit all changes in `data/` and `README.md` to the repository. The commit SHALL use a bot identity.

#### Scenario: Data changed
- **WHEN** the pipeline produces new or updated files
- **THEN** the workflow SHALL configure git with bot user (`github-actions[bot]`)
- **THEN** the workflow SHALL `git add data/ README.md`
- **THEN** the workflow SHALL commit with message `chore: update report YYYY-MM-DD`
- **THEN** the workflow SHALL push to the current branch

#### Scenario: No data changed
- **WHEN** no files are modified after pipeline run
- **THEN** the workflow SHALL skip the commit step without error
- **THEN** the workflow SHALL exit with code 0

### Requirement: Repository permissions
The workflow SHALL request `contents: write` permission for pushing commits and `pages: write` plus `id-token: write` for Pages deployment compatibility.

#### Scenario: Token permissions
- **WHEN** the workflow runs
- **THEN** it SHALL have write access to push commits
- **THEN** it SHALL not require any additional secrets beyond `ANTHROPIC_API_KEY`

### Requirement: Concurrency control
The workflow SHALL use a concurrency group to prevent parallel runs. If a new run starts while a previous one is in progress, the previous run SHALL be cancelled.

#### Scenario: Overlapping runs
- **WHEN** a cron trigger fires while a manual run is in progress
- **THEN** the in-progress run SHALL be cancelled
- **THEN** the new run SHALL proceed

### Requirement: Pages deployment triggered by data push
The workflow SHALL NOT directly deploy to Pages. The existing `report.yml` workflow (triggered on push to `data/**`) SHALL handle Pages deployment automatically.

#### Scenario: Deployment chain
- **WHEN** the pipeline workflow pushes updated `data/` files
- **THEN** the existing Pages deploy workflow SHALL trigger automatically
- **THEN** no duplicate deploy logic SHALL exist in the pipeline workflow
