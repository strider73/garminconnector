# YEHWAN — Athlete Profile

## Basic Information
- **Name**: Yehwan
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 75 kg (165 lbs)
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **BMI**: 22.8 (healthy/athletic)
- **Recent Injury**: Shoulder (fully recovered as of Feb 2026)

## Baseline Metrics

**Dataset:** Mar 6, 2025 - Feb 16, 2026 (348 days, 131 watch-worn days for recovery metrics, 8 GPS errors filtered)

### Recovery Markers (watch-worn days only)
- **Resting HR**: 50.4 ± 3.0 bpm (range: 45-64)
- **HRV (Last Night)**: 69.7 ± 9.4 ms (range: 37-96)
- **HRV (Weekly Average)**: 71.1 ± 5.0 ms (range: 59-83)
- **VO2 Max**: 61.1 ± 2.5 (range: 56-63, excellent for age 20)

### Sleep Patterns
- **Duration**: 6.5 ± 1.4h (range: 2-10h)
- **Sleep Score**: 69.5 ± 14.1 (range: 32-94)
- **Deep Sleep**: 19.3% ± 6.8% (range: 7-44%) — critical for physical recovery
- **REM Sleep**: 15.5% ± 5.9% (range: 3-31%) — critical for mental recovery and skill consolidation
- **Note**: Currently averaging below 7.5h target

### Daily Activity
- **Steps**: 8,788 ± 4,438 (range: 17-22,954)
- **Distance**: 11.2 ± 13.2 km (range: 0-112km)
- **Active Calories**: 759 ± 550 (range: 0-3,081)
- **Moderate Intensity**: 22.2 ± 24.7 mins/day
- **Vigorous Intensity**: 28.1 ± 32.0 mins/day

## Alert Thresholds

### Recovery Alerts
| Metric | Normal Range | Warning | Alert |
|--------|-------------|---------|-------|
| Resting HR | 47-53 bpm | >55 bpm | >56 bpm for 3+ days |
| HRV | 60-79 ms | <56 ms | <51 ms for 3+ days |
| Sleep Duration | 5.1-7.9h | <4h | <3.7h |
| Sleep Score | 55-84 | <48 | <41 |

### Red Flag Actions
When 3+ consecutive days show ANY of:
- HRV <60 ms
- RHR >53 bpm
- Sleep Score <60

**Action:** Drop Wednesday to moderate intensity, skip Sunday PM court session.
See training adjustments: @import .claude/YEHWAN-training-intensity-index.md

## Data Quality Notes
- **Watch-worn detection**: Only days with HRV present and Body Battery >0 are used for recovery metrics
- **GPS errors**: >40km distance with <25 cal/km = forgot to stop activity while driving (ignore distance)
- **Chronic Load**: Garmin API stuck at 219 for 206/346 days — ACWR unreliable, use active calories instead
- **Watch-worn rate**: ~38% of days (131/348) — indicates need for better compliance
