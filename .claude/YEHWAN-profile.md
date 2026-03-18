# YEHWAN — Athlete Profile

## Basic Information
- **Name**: Yehwan
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 75 kg (165 lbs)
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **BMI**: 22.8 (healthy/athletic)
- **Recent Injury**: Shoulder (fully recovered as of Feb 2026)
- **Telegram Chat ID**: 8419192509
- **Coach (Chris) Telegram Chat ID**: 8681791219

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
- **Steps**: 12,943 ± 4,438 (range: 17-22,954) *(updated Mar 2026 — 2-week healthy baseline)*
- **Active Calories**: 1,414 ± 550 (range: 0-3,081) *(updated Mar 2026 — 2-week healthy baseline)*
- **Moderate Intensity**: 44 ± 25 mins/day *(updated Mar 2026 — 2-week healthy baseline)*
- **Vigorous Intensity**: 51 ± 32 mins/day *(updated Mar 2026 — 2-week healthy baseline)*

### Yearly Goal — 30% Increase by End of 2026
- **Target Active Calories**: 1,838/day (1,414 × 1.30)
- **Target Steps**: 16,826/day (12,943 × 1.30)
- **Weekly progression**: 0.5-1% increase per week (~7-14 cal/day)
- **Baseline set**: March 2026 (post-injury, 2-week healthy average)

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

## Tennis HR Fingerprint

**Dataset:** 16 full tennis sessions (≥60 min) from Feb 13–27, 2026

Use this fingerprint to detect unlogged tennis sessions from raw heart rate data.

### During-Play Signature
| Metric | Value | Notes |
|--------|-------|-------|
| Avg HR | 129 ± 13 bpm (range: 114–156) | Core identifier |
| Max HR spikes | 166–204 bpm | Hits 160+ every full session |
| HR variability (StdDev) | 17–33 bpm | High — interval nature (rallies + changeovers) |
| HR jump between readings | ~10 bpm avg; 28–46% are ≥10 bpm | Distinguishes from steady-state cardio |
| Time ≥ 100 bpm | 58–100% of session | |
| Time ≥ 120 bpm | 42–97% of session | |
| Time ≥ 140 bpm | 21–79% of session | |
| Session duration | 80–204 min (avg 137 min) | |
| Cal burn rate | 5.5–10.5 cal/min | |

### Transition Markers
| Phase | HR | Notes |
|-------|-----|-------|
| Pre-tennis (resting) | 76–85 bpm | Sharp jump at session start |
| Post-tennis (1h after) | 93–108 bpm | Drops to 70s within 30 min |

### Detection Algorithm
To identify unlogged tennis from raw HR data:
1. **Sustained elevation**: HR ≥ 100 bpm for ≥ 30 consecutive minutes
2. **Avg HR in window**: 110–160 bpm
3. **High variability**: StdDev ≥ 15 bpm (interval pattern, not steady-state)
4. **Peak spikes**: At least some readings ≥ 150 bpm
5. **Minimum duration**: ≥ 60 min for a real session

> **Key differentiator**: The high HR variability separates tennis from running (steady HR) and strength training (short bursts + long rest). Tennis shows a unique oscillating pattern of rallies (HR spikes) and changeovers (HR drops).

## Tennis Fitness Progression (Updated 2026-03-12)

**Full report:** `reports/tennis_fitness_progression.md`

### Timeline
| Phase | Period | Sessions/mo | Avg HR | Notes |
|-------|--------|-------------|--------|-------|
| Peak training | Mar–Jun 2025 | 24 | 123–128 | Full volume, pre-injury |
| Injury break | Jul–Sep 2025 | 0 | — | Shoulder injury |
| Tentative return | Oct–Dec 2025 | 3 | 118–136 | Easing back |
| Low volume | Jan 2026 | 2 | 112 | Cautious |
| Full comeback | Feb 2026 | 22 | 121 | Rapid ramp to near-peak |

### February 2026 Ramp-Up (Key Evidence)
| Week | Sessions | Court Min | Avg HR | Max HR | Cal/min |
|------|----------|-----------|--------|--------|---------|
| Week 1 (Feb 1–12) | 4 | 473 | 103 | 184 | 4.7 |
| Week 2 (Feb 13–19) | 9 | 900 | 121 | 195 | 6.3 |
| Week 3 (Feb 20–28) | 9 | 1,365 | 130 | 204 | 6.9 |

### Fitness Growth Indicators
- Max HR ceiling: 182 (Jan) → 204 (Feb) = **+22 bpm capacity**
- Volume: 2 → 22 sessions/month
- Court time: 208 → 2,738 min/month **(13× increase)**
- Late Feb comparable sessions **match Mar 2025 pre-injury intensity**
- VO2 Max: 61.1 baseline → 56.3 current (expected post-break dip, recovering)

## Data Quality Notes
- **Watch-worn detection**: Only days with HRV present and Body Battery >0 are used for recovery metrics
- **GPS errors**: >40km distance with <25 cal/km = forgot to stop activity while driving (ignore distance)
- **Chronic Load**: Garmin API stuck at 219 for 206/346 days — ACWR unreliable, use active calories instead
- **Watch-worn rate**: ~38% of days (131/348) — indicates need for better compliance
