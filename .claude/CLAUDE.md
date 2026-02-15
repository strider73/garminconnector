# Yehwan's Training Guide — GarminConnector Project

## Purpose
Data-driven training management system for Yehwan, built on Garmin Connect APIs. Automated daily reports, readiness scoring, and AI coaching via n8n workflows.

## Athlete Profile
- **Name**: Yehwan
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 75 kg (165 lbs)
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **Resting HR**: ~44 bpm (athlete range)
- **VO2 Max**: 56.6 (measured 2026-01-28)
- **BMI**: 22.8 (healthy/athletic)
- **Recent Injury**: Shoulder (fully recovered as of Feb 2026)

## Automated Pipelines (n8n on Raspberry Pi)

| Time | Workflow | What it does |
|------|----------|--------------|
| 9:30pm | Store Daily Metrics | Garmin → PostgreSQL (garmin_daily_metrics) |
| 10:00pm | Daily Report + AI | Full report → Gemini analysis → Email + SMS |
| 7:30am | Morning Readiness + AI | Readiness score → Gemini coaching → Email + SMS |

## AI Coach Prompts (Gemini 2.5 Flash)
The AI coach receives the full report and provides:
1. **Day comparison** — today's metrics vs 7-day trend (sleep, HRV, RHR, ACWR, body battery)
2. **Training plan** — recommended hours and intensity based on readiness score:
   - PRIME (80+): 2-3h high intensity (match play, hard drills)
   - MODERATE (60-79): 1.5-2h moderate (technical work, light hitting)
   - LOW (40-59): 1h light only (stretching, easy rallying)
   - POOR (<40): Rest day or 30min light movement

## Key Metrics & Thresholds
- **ACWR sweet spot**: 0.8–1.3 (injury risk above 1.5)
- **Sleep target**: 7.5h minimum, 8h on pre-match nights
- **HRV red flag**: below 55 for 3+ consecutive days
- **RHR red flag**: above 55 for 3+ consecutive days
- **Red flag action**: drop Wednesday to moderate, skip Sunday PM court

## References
@import .claude/Yewhan_weekly_schedule.md
@import .claude/python-scripts-reference.md
@import /Users/chrislee/.claude/shared/n8n-mcp-instructions.md