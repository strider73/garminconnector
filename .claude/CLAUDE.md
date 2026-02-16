# Yehwan's Training Guide — GarminConnector Project

## Purpose
Data-driven training management system for Yehwan, built on Garmin Connect APIs. Automated daily reports, readiness scoring, and AI coaching via n8n workflows.

## Athlete Profile
See detailed baseline metrics and thresholds: @import .claude/yehwan-profile.md
See training intensity patterns and court time: @import .claude/yehwan-training-intensity-pattern.md

**Quick Reference:**
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
| 7:30am | Morning Readiness + AI | Readiness score → AI coaching → Email + SMS |

## AI Coach Prompts
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