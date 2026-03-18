# Store Daily Metrics Output Template

This is the output structure produced by `store_daily_metrics.py`.
The script prints this to stdout. No email/Telegram — n8n just logs it.

```
Connecting to Garmin...
Connected as: {full_name}

Fetching metrics for {YYYY-MM-DD}...
Stored: {YYYY-MM-DD} (steps={XXXXX}, acute_load={XXX}, sleep={X.XX}h, sleep_score={XX})

Done.
```

## With --backfill flag

```
Fetching metrics for {YYYY-MM-DD}...
Stored: {YYYY-MM-DD} (steps={XXXXX}, acute_load={XXX}, sleep={X.XX}h, sleep_score={XX})
Fetching metrics for {YYYY-MM-DD}...
Stored: {YYYY-MM-DD} (steps={XXXXX}, acute_load={XXX}, sleep={X.XX}h, sleep_score={XX})
(repeated for each day)

Done.
```

## What Gets Stored (PostgreSQL `garmin_daily_metrics` table)

| Category | Fields |
|----------|--------|
| Identity | user_name, report_date |
| Training Load | training_status, training_feedback, status_since, acute_load, chronic_load, acwr_ratio, acwr_status, acwr_percent |
| VO2 Max | vo2_max, vo2_max_date, balance_feedback |
| Intensity Zones | aerobic_low/high, anaerobic (+ target min/max for each) |
| HRV | hrv_last_night, hrv_weekly_avg, hrv_status |
| Sleep | sleep_hours, deep/light/rem/awake mins, sleep_start/end, sleep_score, sleep_quality, sleep_*_percentage, sleep_feedback, sleep_insight |
| Heart Rate | resting_hr, max_hr, min_hr |
| Body/Stress | body_battery_charged/drained, max_stress |
| Activity | total_steps, total_distance_km, total_calories, active_calories, moderate/vigorous_intensity_mins, floors_climbed |

## Data Sources (Garmin API)
- `garmin.get_training_status(date)` → training load, VO2, zones, balance
- `garmin.get_hrv_data(date)` → HRV metrics
- `garmin.get_sleep_data(date)` → all sleep fields
- `garmin.get_heart_rates(date)` → HR metrics
- `garmin.get_stress_data(date)` → stress
- `garmin.get_body_battery(date)` → body battery
- `garmin.get_stats(date)` → steps, distance, calories, intensity
