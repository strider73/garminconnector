# GarminConnector

Yehwan wears a Garmin watch every day. This project turns that raw watch data — sleep, HRV, resting heart rate, training load, workouts — into something a coach would actually say to him: how recovered he is this morning, whether today should be a hard session or a rest day, and how the week is trending.

Nothing here is manual. Five n8n workflows run on a schedule, each one SSHing into a Raspberry Pi to run a Python script against the Garmin Connect API, storing the results in PostgreSQL and handing the numbers to Claude to turn into a short, personal coaching message. Two of the five stop at "store the data" or "check the pipeline is healthy" — the other three go all the way to Yehwan's inbox and phone: a morning readiness check before he trains, a nightly recap of how the day actually went, and a weekly PDF for his coach.

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

Five n8n workflows, all live on the same n8n instance, each doing one job on a fixed schedule:

**Garmin Store Daily Metrics — 9:00pm daily**
Pulls the day's full metrics from Garmin (training load, HRV, sleep stages, resting HR, body battery, stress, steps/calories) and upserts them into the `garmin_daily_metrics` table. Right after, it regenerates Yehwan's baseline reference files (`YEHWAN-profile.md`, `YEHWAN-training-intensity-index.md`) from the updated history, so every AI coaching message from that point on is comparing against current numbers, not stale ones. No email, no AI — this workflow just keeps the data warehouse and the baselines honest.

**Garmin Daily Report — 9:30pm daily**
Fetches today's full breakdown (sleep, activity, heart rate, stress, workouts) plus the last 7 days for context, then hands it to Claude to classify the day's intensity, check recovery against baseline, and recommend tomorrow's training. Goes out as an email to Chris and Yehwan (raw data + AI analysis) and a short Telegram message to both with just the coaching text.

**Garmin Morning Readiness — weekday + Sunday 8:00am, Saturday 9:00am**
Same idea but first thing in the morning: overnight HRV, sleep, resting HR, body battery, plus yesterday's load. Garmin's sleep data isn't always ready by 8am, so this one has a retry loop built in — it waits 30 minutes and checks again, up to 4 hours, before generating the coaching message. Same delivery: email with data + AI, Telegram with AI only.

**HR Collection Health Monitor — every 3 hours**
Not a coaching workflow — a watchdog. A separate cron job on the server pulls heart rate readings roughly every 2 minutes; this workflow just checks PostgreSQL for any reading in the last 3 hours. If nothing shows up, it alerts Chris and Yehwan on Telegram that the watch might not be worn or the collection job might have died.

**Weekly Trainer Report — Thursday 8:00am**
Builds a 7-day PDF (activity charts, HR/recovery trends, training load, sleep table) straight from Python and matplotlib — no AI step. Emailed to Chris as a quick read before Thursday's session with the trainer.

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
