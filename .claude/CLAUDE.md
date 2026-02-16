# Yehwan's Training Guide — GarminConnector Project

## Purpose
Data-driven training management system for Yehwan, built on Garmin Connect APIs. Automated daily reports, readiness scoring, and AI coaching via n8n workflows.

## Athlete Profile
- **Name**: Yehwan
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 75 kg (165 lbs)
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **BMI**: 22.8 (healthy/athletic)
- **Recent Injury**: Shoulder (fully recovered as of Feb 2026)

### Baseline Performance Metrics (Cleaned Dataset: Mar 6, 2025 - Feb 16, 2026)
Data from 340 days (120 watch-worn days for recovery metrics, 8 GPS errors filtered)

**Recovery Markers:**
- **Resting HR**: 50.4 ± 3.0 bpm (range: 45-64, baseline target: 44)
- **HRV**: 69.9 ± 9.4 ms (range: 37-96, normal: 50-89)
- **HRV Weekly Avg**: 71.3 ± 5.0 ms (range: 59-83)
- **VO2 Max**: 60.4 ± 2.5 (range: 56-63, excellent for age 20)

**Sleep Patterns:**
- **Duration**: 6.5 ± 1.4h (range: 2-10h, target: 7.5h+)
- **Sleep Score**: 69.5 ± 14.3 (range: 32-94)
- **Deep Sleep**: 19.3% ± 7.1% (range: 0-44%)
- **REM Sleep**: 15.0% ± 6.5% (range: 0-31%)

**Daily Activity:**
- **Steps**: 8,751 ± 4,471 (range: 17-22,954)
- **Distance**: 8.8 ± 6.2 km (range: 0-39km, GPS errors >40km filtered)
- **Active Calories**: 744 ± 544 (range: 0-3,081)
- **Moderate Intensity**: 21.9 ± 24.8 mins
- **Vigorous Intensity**: 26.8 ± 31.0 mins

**Training Load:**
- **ACWR**: 0.4 ± 0.5 (range: 0-2.9, safe zone: 0.8-1.3)
- **Acute Load**: 317 ± 463 (range: 0-1,719, highly variable)
- **Chronic Load**: 463 ± 426 (range: 100-1,707)

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
**Training Load:**
- **ACWR sweet spot**: 0.8–1.3 (injury risk above 1.5, alert if >1.9)
- **Safe training zone**: Acute load should stay within 0.8-1.3x chronic load

**Recovery Markers:**
- **RHR alert**: >57 bpm (normal: 44-56 bpm)
- **HRV alert**: <50 or >89 ms (outside 95% confidence)
- **Sleep target**: 7.5h minimum, 8h on pre-match nights
- **Sleep score alert**: <41 (poor recovery)

**Outlier Detection (flag for review):**
- **RHR**: Alert if <44 or >57 bpm (outside mean ± 2σ on watch-worn days)
- **HRV**: Alert if <51 or >88 ms (outside mean ± 2σ)
- **Sleep Duration**: Alert if <3.7h or >9.3h (outside mean ± 2σ)
- **Sleep Score**: Alert if <41 (poor recovery, outside mean - 2σ)
- **Steps**: Alert if >17,692 (outside mean + 2σ)
- **Distance**: Alert if >40km with <25 cal/km (GPS error = forgot to stop activity while driving)
- **ACWR**: Alert if >1.4 (outside mean + 2σ), critical if >1.9 (injury risk zone)

**Red Flag Actions:**
- 3+ consecutive days: HRV <55, RHR >55, or Sleep Score <60
- Action: Drop Wednesday to moderate intensity, skip Sunday PM court session

## References
@import .claude/Yewhan_weekly_schedule.md
@import .claude/python-scripts-reference.md
@import /Users/chrislee/.claude/shared/n8n-mcp-instructions.md