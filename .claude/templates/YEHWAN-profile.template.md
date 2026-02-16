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

**Dataset:** {first_date} - {last_date} ({total_days} days, {watch_worn_days} watch-worn days for recovery metrics, {gps_errors} GPS errors filtered)

### Recovery Markers (watch-worn days only)
- **Resting HR**: {rhr_mean} ± {rhr_std} bpm (range: {rhr_min}-{rhr_max})
- **HRV (Last Night)**: {hrv_mean} ± {hrv_std} ms (range: {hrv_min}-{hrv_max})
- **HRV (Weekly Average)**: {hrv_wk_mean} ± {hrv_wk_std} ms (range: {hrv_wk_min}-{hrv_wk_max})
- **VO2 Max**: {vo2_mean} ± {vo2_std} (range: {vo2_min}-{vo2_max}, excellent for age 20)

### Sleep Patterns
- **Duration**: {sleep_hrs_mean} ± {sleep_hrs_std}h (range: {sleep_hrs_min}-{sleep_hrs_max}h)
- **Sleep Score**: {sleep_score_mean} ± {sleep_score_std} (range: {sleep_score_min}-{sleep_score_max})
- **Deep Sleep**: {deep_pct_mean}% ± {deep_pct_std}% (range: {deep_pct_min}-{deep_pct_max}%) — critical for physical recovery
- **REM Sleep**: {rem_pct_mean}% ± {rem_pct_std}% (range: {rem_pct_min}-{rem_pct_max}%) — critical for mental recovery and skill consolidation
- **Note**: Currently averaging below 7.5h target

### Daily Activity
- **Steps**: {steps_mean} ± {steps_std} (range: {steps_min}-{steps_max})
- **Distance**: {dist_mean} ± {dist_std} km (range: {dist_min}-{dist_max}km)
- **Active Calories**: {acal_mean} ± {acal_std} (range: {acal_min}-{acal_max})
- **Moderate Intensity**: {mod_mins_mean} ± {mod_mins_std} mins/day
- **Vigorous Intensity**: {vig_mins_mean} ± {vig_mins_std} mins/day

## Alert Thresholds

### Recovery Alerts
| Metric | Normal Range | Warning | Alert |
|--------|-------------|---------|-------|
| Resting HR | {rhr_normal_lo}-{rhr_normal_hi} bpm | >{rhr_warning} bpm | >{rhr_alert} bpm for 3+ days |
| HRV | {hrv_normal_lo}-{hrv_normal_hi} ms | <{hrv_warning} ms | <{hrv_alert} ms for 3+ days |
| Sleep Duration | {sleep_normal_lo}-{sleep_normal_hi}h | <{sleep_warning}h | <{sleep_alert}h |
| Sleep Score | {score_normal_lo}-{score_normal_hi} | <{score_warning} | <{score_alert} |

### Red Flag Actions
When 3+ consecutive days show ANY of:
- HRV <{hrv_red_flag} ms
- RHR >{rhr_red_flag} bpm
- Sleep Score <{score_red_flag}

**Action:** Drop Wednesday to moderate intensity, skip Sunday PM court session.
See training adjustments: @import .claude/YEHWAN-training-intensity-index.md

## Data Quality Notes
- **Watch-worn detection**: Only days with HRV present and Body Battery >0 are used for recovery metrics
- **GPS errors**: >40km distance with <25 cal/km = forgot to stop activity while driving (ignore distance)
- **Chronic Load**: Garmin API stuck at 219 for 206/346 days — ACWR unreliable, use active calories instead
- **Watch-worn rate**: ~{watch_worn_pct}% of days ({watch_worn_days}/{total_days}) — indicates need for better compliance
