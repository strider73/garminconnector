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

### Baseline Performance Metrics (400-day analysis: Mar 2025 - Feb 2026)
**Recovery Markers:**
- **Resting HR**: 50 ± 3 bpm (range: 45-64, baseline target: 44)
- **HRV**: 70 ± 10 ms (range: 37-96, normal: 50-89)
- **VO2 Max**: 60.4 ± 2.5 (range: 56-63, excellent for age)

**Sleep Patterns:**
- **Duration**: 6.5 ± 1.4h (range: 2.4-9.6h, target: 7.5h+)
- **Sleep Score**: 70 ± 14 (range: 32-94)
- **Deep Sleep**: 19% ± 7% (range: 0-44%)
- **REM Sleep**: 15% ± 7% (range: 0-31%)

**Daily Activity:**
- **Steps**: 8,750 ± 4,470 (range: 17-22,954)
- **Distance**: 8.8 ± 6.2 km (range: 0-39km, GPS errors filtered)
- **Active Calories**: 744 ± 544 (range: 0-3,081)
- **Moderate Intensity**: 22 ± 25 mins
- **Vigorous Intensity**: 27 ± 31 mins

**Training Load:**
- **ACWR**: Typically 0.2-1.4 (mean: 0.4, safe zone: 0.8-1.3)
- **Acute Load**: Highly variable (0-1,719)
- **Chronic Load**: 219-698 typical range

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
- **RHR**: Alert if <41 or >59 bpm
- **HRV**: Alert if <41 or >98 ms
- **Sleep**: Alert if <2.3h or >10.7h
- **Steps**: Alert if >22,000 (possible GPS error if distance also high)
- **Distance**: Alert if >40km with <25 cal/km (GPS error = forgot to stop activity while driving)

**Red Flag Actions:**
- 3+ consecutive days: HRV <55, RHR >55, or Sleep Score <60
- Action: Drop Wednesday to moderate intensity, skip Sunday PM court session

## References
@import .claude/Yewhan_weekly_schedule.md
@import .claude/python-scripts-reference.md
@import /Users/chrislee/.claude/shared/n8n-mcp-instructions.md