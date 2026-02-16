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

**Dataset:** Mar 6, 2025 - Feb 16, 2026 (340 days, 120 watch-worn days for recovery metrics, 8 GPS errors filtered)

### Recovery Markers (watch-worn days only)
- **Resting HR**: 50.4 ± 3.0 bpm (range: 45-64)
- **HRV (Last Night)**: 69.9 ± 9.4 ms (range: 37-96)
- **HRV (Weekly Average)**: 71.3 ± 5.0 ms (range: 59-83)
- **VO2 Max**: 60.4 ± 2.5 (range: 56-63, excellent for age 20)

### Sleep Patterns
- **Duration**: 6.5 ± 1.4h (range: 2-10h)
- **Sleep Score**: 69.5 ± 14.3 (range: 32-94)
- **Deep Sleep**: 19.3% ± 7.1% (range: 0-44%) — critical for physical recovery
- **REM Sleep**: 15.0% ± 6.5% (range: 0-31%) — critical for mental recovery and skill consolidation
- **Note**: Currently averaging below 7.5h target

### Daily Activity
- **Steps**: 8,751 ± 4,471 (range: 17-22,954)
- **Distance**: 8.8 ± 6.2 km (range: 0-39km)
- **Active Calories**: 744 ± 544 (range: 0-3,081)
- **Moderate Intensity**: 21.9 ± 24.8 mins/day
- **Vigorous Intensity**: 26.8 ± 31.0 mins/day

## Alert Thresholds

### Recovery Alerts
| Metric | Normal Range | Warning | Alert |
|--------|-------------|---------|-------|
| Resting HR | 47-53 bpm | >57 bpm | >60 bpm for 3+ days |
| HRV | 51-88 ms | <51 ms | <55 ms for 3+ days |
| Sleep Duration | 5.1-7.9h | <5h | <3.7h |
| Sleep Score | 55-84 | <55 | <41 |

### Red Flag Actions
When 3+ consecutive days show ANY of:
- HRV <55 ms
- RHR >55 bpm
- Sleep Score <60

**Action:** Drop Wednesday to moderate intensity, skip Sunday PM court session.
See training adjustments: @import .claude/YEHWAN-training-intensity-index.md

## Data Quality Notes
- **Watch-worn detection**: Only days with HRV present and Body Battery >0 are used for recovery metrics
- **GPS errors**: >40km distance with <25 cal/km = forgot to stop activity while driving (ignore distance)
- **Chronic Load**: Garmin API stuck at 219 for 206/346 days — ACWR unreliable, use active calories instead
- **Watch-worn rate**: ~35% of days (120/340) — indicates need for better compliance
