# Yehwan's Training Guide — GarminConnector Project

## Purpose
Data-driven training management system for Yehwan, built on Garmin Connect APIs. Automated daily reports, readiness scoring, and AI coaching via n8n workflows.

## How the System Works
```
n8n (scheduler) → SSH → Docker runs Python script → stdout (raw Garmin data)
                → SSH → Claude CLI + /command < raw data → stdout (AI coaching)
                → Combines both → Email (data + AI) + Telegram (AI only)
```
1. **n8n** triggers on schedule and SSHs into the server
2. **Docker** runs a Python script that pulls from Garmin API and prints raw data to stdout
3. **n8n** captures that output and pipes it into **Claude CLI** with a slash command
4. **Claude** reads the raw data + reference files (`.claude/reference/`) and outputs coaching text
5. **n8n** combines both outputs into an email and sends via Gmail + Telegram

Scripts live in `n8n-workflows/`, commands in `.claude/commands/`, reference data in `.claude/reference/`.

## Athlete Quick Reference
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **Age**: 20 | **Height**: 6'1" | **Weight**: 75kg
- **Resting HR**: 50 ± 3 bpm | **HRV**: 70 ± 9 ms | **VO2 Max**: 60.4 ± 2.5
- **Sleep**: 6.5 ± 1.4h (target: 7.5h+) | **Sleep Score**: 70 ± 14
- **Daily Steps**: 8,751 ± 4,471 | **Active Calories**: 744 ± 544
- **Typical Training Week**: 12-15h court time (periodized: rest 17%, light 22%, moderate 24%, hard 23%, very hard 15%)

## Automated Pipelines (n8n on Raspberry Pi)

| Time | Workflow | What it does |
|------|----------|--------------|
| 9:30pm | Store Daily Metrics | Garmin → PostgreSQL (garmin_daily_metrics) |
| 10:00pm | Daily Report + AI | Full report → AI analysis → Email + SMS |
| 8:00am (Sat 9:00am) | Morning Readiness + AI | Readiness score → AI coaching → Email + SMS |

## AI Coach
The AI coach uses Yehwan's personal data (profile, training intensity index, weekly schedule) to provide:
1. **Day classification** — classify today's intensity using the Training Intensity Index
2. **Day comparison** — today's metrics vs personal baselines (not generic thresholds)
3. **Training block context** — last 7 days pattern (consecutive hard days, loading vs recovery)
4. **Tomorrow's recommendation** — specific intensity level, court time, session count, activities

## References
- Project structure & file rules: @import project_structure.md
- Athlete profile, baselines & alert thresholds: @import .claude/reference/YEHWAN-profile.md
- Training intensity index & load monitoring: @import .claude/reference/YEHWAN-training-intensity-index.md
- Weekly schedule & session times: @import .claude/reference/YEHWAN-weekly-schedule.md
- AI coaching logic & prompt templates: @import .claude/commands/not-used/ai-coaching-template.md
- Python scripts: @import .claude/reference/python-scripts-reference.md
- n8n instructions: @import /Users/chrislee/.claude/shared/n8n-mcp-instructions.md