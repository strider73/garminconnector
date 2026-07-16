# GarminConnector

Data-driven training management system for Yehwan, an advanced tennis player (UTR 8). Pulls daily data from Garmin Connect, scores training readiness, and generates AI coaching reports — fully automated via n8n and Claude Code.

## How It Works

```
n8n (scheduler) → SSH → Docker runs Python script → stdout (raw Garmin data)
                → SSH → Claude CLI + /command < raw data → stdout (AI coaching)
                → Combines both → Email (data + AI) + Telegram (AI only)
```

1. **n8n** triggers on a schedule and SSHs into the server
2. **Docker** runs a Python script that pulls from the Garmin API and prints raw data to stdout
3. **n8n** captures that output and pipes it into **Claude CLI** with a slash command
4. **Claude** reads the raw data plus athlete reference files (`.claude/reference/`) and outputs coaching text
5. **n8n** combines both outputs into an email (Gmail) and a Telegram message

## Automated Workflows

| Time | Workflow | What it does |
|------|----------|---------------|
| 9:30pm | Store Daily Metrics | Garmin → PostgreSQL (`garmin_daily_metrics`) |
| 10:00pm | Daily Report + AI | Full report → AI analysis → Email + SMS |
| 8:00am (Sat 9:00am) | Morning Readiness + AI | Readiness score → AI coaching → Email + SMS |
| Every 3h | HR Health Monitor | Heart rate data → PostgreSQL |
| Thursday 8am | Weekly Trainer Report | PDF with activity timeline, sleep table, AI briefings |

## Project Structure

```
GarminConnector/
├── n8n-workflows/          # One folder per n8n workflow (script + process doc + template)
├── garminconnect/          # Garmin Connect API client library (shared by all scripts)
├── .claude/
│   ├── commands/            # Claude Code slash commands (AI coaching prompts)
│   ├── reference/           # Athlete baselines, intensity index, weekly schedule
│   ├── templates/           # Templates for auto-generated reference files
│   └── agents/               # Agent that regenerates baselines from PostgreSQL
├── custom_scripts/one-off/  # Archived one-off analysis scripts
├── Dockerfile / docker-compose.yml
├── Jenkinsfile               # CI/CD pipeline
├── create_garmin_table.sql
└── config.example.py         # Credential template (copy to config.py)
```

See `project_structure.md` for the full file map and folder rules.

## Setup

```bash
cp config.example.py config.py   # fill in Garmin credentials + DB connection
pip install -e .
```

## Testing Locally

```
/n8n-daily-report-930pm             # script + AI coaching
/n8n-morning-readiness-8am          # script + AI coaching
/n8n-store-daily-metrics-9pm        # script only
/n8n-hr-health-monitor-3h           # script only
/n8n-weekly-trainer-report-thu-8am  # script only, needs Docker for matplotlib
```

## Deployment

Fully automated: `git push` → GitHub webhook → Jenkins → syncs `.claude/` on the host and rebuilds the Docker image. See `DEPLOYMENT.md` for the full architecture, SSH key setup, and manual fallback steps.

## Athlete Profile

- Sport: Tennis (UTR 8) · Age 20 · 6'1" · 75kg
- Resting HR 50±3 bpm · HRV 70±9 ms · VO2 Max 60.4±2.5
- Sleep 6.5±1.4h (target 7.5h+) · Sleep Score 70±14
- Training week: 12–15h court time, periodized load

Full baselines and alert thresholds live in `.claude/reference/YEHWAN-profile.md`.
