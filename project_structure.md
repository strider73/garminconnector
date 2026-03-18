# Project Structure

## Rules
- New workflow scripts go in `n8n-workflows/<workflow-name>/`
- New AI coaching commands go in `.claude/commands/`
- New athlete reference data goes in `.claude/reference/`
- New baseline templates go in `.claude/templates/`
- One-off/experimental scripts go in `custom_scripts/one-off/`
- Generated files (PDFs, reports) are gitignored — keep one `sample-*` as example
- Each workflow folder must contain: the script, a `*-process.md`, and a `*-template.md`

## Folder Map

```
GarminConnector/
│
├── n8n-workflows/                    ← One folder per n8n workflow
│   ├── daily-report-930pm/           ← Garmin Daily Report - 9:30pm Email
│   │   ├── daily_report.py           ← Python script (fetches Garmin data, prints report)
│   │   ├── daily-report-process.md   ← How the pipeline works end-to-end
│   │   └── daily-report-template.md  ← What the script output looks like
│   │
│   ├── morning-readiness-8am/        ← Morning Readiness - Weekday+Sun 8am, Sat 9am
│   │   ├── training_readiness.py     ← Python script (readiness score + recovery data)
│   │   ├── morning-readiness-process.md
│   │   └── morning-readiness-template.md
│   │
│   ├── store-daily-metrics-9pm/      ← Store Daily Metrics - 9pm
│   │   ├── store_daily_metrics.py    ← Python script (Garmin → PostgreSQL)
│   │   ├── store-daily-metrics-process.md
│   │   └── store-daily-metrics-template.md
│   │
│   ├── hr-health-monitor-3h/         ← HR Collection Health Monitor - 3H interval
│   │   ├── store_heartrate.py        ← Python script (HR data → PostgreSQL, runs via cron)
│   │   ├── hr-health-monitor-process.md
│   │   └── hr-health-monitor-template.md
│   │
│   └── weekly-trainer-report-thu-8am/ ← Weekly Trainer Report - Thursday 8am
│       ├── trainer_report.py          ← Python script (generates PDF with charts)
│       ├── weekly-trainer-report-process.md
│       ├── weekly-trainer-report-template.md
│       └── sample-report.pdf          ← Example output (only sample PDFs are committed)
│
├── .claude/                           ← Claude Code configuration and data
│   ├── CLAUDE.md                      ← Project instructions (must stay at this path)
│   │
│   ├── commands/                      ← Claude Code slash commands (auto-discovered)
│   │   ├── daily-coaching-email.md    ← /daily-coaching-email (used by daily report workflow)
│   │   ├── morning-readiness.md       ← /morning-readiness (used by morning readiness workflow)
│   │   ├── daily-coaching-sms.md      ← /daily-coaching-sms (available, not wired to n8n)
│   │   ├── morning-readiness-sms.md   ← /morning-readiness-sms (available, not wired to n8n)
│   │   └── ai-coaching-template.md    ← Reference doc for coaching logic
│   │
│   ├── reference/                     ← Athlete data files (read by commands at runtime)
│   │   ├── YEHWAN-profile.md          ← Baselines, alert thresholds, HR fingerprint
│   │   ├── YEHWAN-training-intensity-index.md ← Intensity classification, load thresholds
│   │   ├── YEHWAN-weekly-schedule.md  ← Weekly session times and schedule
│   │   └── python-scripts-reference.md ← Script documentation
│   │
│   ├── templates/                     ← Templates for auto-generated reference files
│   │   ├── YEHWAN-profile.template.md
│   │   └── YEHWAN-training-intensity-index.template.md
│   │
│   ├── agents/                        ← Claude Code agents
│   │   ├── update-baselines.md        ← Agent definition
│   │   └── scripts/
│   │       └── update_baselines.py    ← Queries PostgreSQL, regenerates reference files
│   │
│   └── settings.local.json            ← Local Claude Code settings
│
├── garminconnect/                     ← Garmin API client library (shared by all scripts)
│   ├── __init__.py                    ← Main Garmin class (login, all API methods)
│   ├── fit.py                         ← FIT file parser
│   └── workout.py                     ← Workout builder
│
├── custom_scripts/
│   └── one-off/                       ← Archived one-off analysis scripts (not used by workflows)
│
├── Dockerfile                         ← Builds garmin-report container
├── docker-compose.yml                 ← Defines garmin-report service
├── Jenkinsfile                        ← CI/CD pipeline
├── config.py                          ← Garmin credentials + DB connection (not committed)
├── config.example.py                  ← Credential template
├── create_garmin_table.sql            ← Database schema
├── pyproject.toml                     ← Python project config
├── .mcp.json                          ← MCP server config (n8n, PostgreSQL)
├── .gitignore
└── project_structure.md               ← This file
```

## How Workflows Use Files

| Workflow | Script | Command | Reference Files |
|----------|--------|---------|-----------------|
| daily-report-930pm | `daily_report.py` | `/daily-coaching-email` | profile, intensity index |
| morning-readiness-8am | `training_readiness.py` | `/morning-readiness` | profile, intensity index, weekly schedule |
| store-daily-metrics-9pm | `store_daily_metrics.py` + `update_baselines.py` | none | templates → reference (output) |
| hr-health-monitor-3h | `store_heartrate.py` | none | none |
| weekly-trainer-report-thu-8am | `trainer_report.py` | none | none |
