# Morning Readiness Output Template

This is the output structure produced by `training_readiness.py`.
The script prints this to stdout, which n8n captures and sends via email/Telegram.

```
Connecting to Garmin...
Connected as: {full_name}

=======================================================
  1. RECOVERY - {YYYY-MM-DD}
=======================================================

  VO2 Max:          {XX.X}
    Measured:       {YYYY-MM-DD}
    Fitness Age:    {XX}

  Training Status:  {PRODUCTIVE/MAINTAINING/RECOVERY/etc}
    Feedback:       {feedback phrase}
    Since:          {YYYY-MM-DD}

  --- Training Load ---
  Acute Load:       {XXX}
  Chronic Load:     {XXX}
  Acute/Chronic:    {X.XX}
  Load Status:      {OPTIMAL/HIGH/LOW} ({XX}%)

  --- Monthly Load Balance ---
  Aerobic Low:      {XXX.X} (target: {XXX}-{XXX})
  Aerobic High:     {XXX.X} (target: {XXX}-{XXX})
  Anaerobic:        {XXX.X} (target: {XXX}-{XXX})
  Feedback:         {balance feedback phrase}

  --- Sleep Timing (last night) ---
  Bed Time:         {HH:MM AM/PM, Day Mon DD}
  Wake Time:        {HH:MM AM/PM, Day Mon DD}
  Duration:         {X.X}h
  Sleep Score:      {XX}
  Sleep Quality:    {GOOD/FAIR/POOR/EXCELLENT}
  Feedback:         {sleep feedback}
  [SLEEP_STATUS:{COMPLETE/PENDING/NOT_WORN/NO_DATA}]

  --- Heart Rate (live API) ---
  Resting HR:       {XX}

  --- HRV (live API) ---
  Last Night:       {XX}
  Weekly Avg:       {XX}
  Status:           {BALANCED/LOW/etc}

  --- Body Battery (live API) ---
  Charged:          {XX}
  Drained:          {XX}

=======================================================
  3. TRAINING READINESS - {YYYY-MM-DD}
=======================================================

  Readiness Score:  {XX}/100  [{PRIME/MODERATE/LOW/POOR}]
  -> {recommendation message}

  --- Factor Breakdown ---
  Load Balance   {XX}/100  [{###########....}]  (ACWR {X.X})
  Sleep          {XX}/100  [{###########....}]  (Sleep score {XX})
  HRV Recovery   {XX}/100  [{###########....}]  (HRV {XX} (avg {XX}))
  Resting HR     {XX}/100  [{###########....}]  (RHR {XX} (base {XX}))
  Body Battery   {XX}/100  [{###########....}]  (BB charged {XX})

=======================================================
  4. 7-DAY TRENDS
=======================================================

  Date         Load  ACWR Sleep     Bed    Wake  RHR   HRV  BB+  Steps ActCal Stress
  ------------ ------ ----- ----- ------- ------- ---- ----- ---- ------ ------ ------
  {YYYY-MM-DD} {XXX}  {X.X} {X.X} {H:MMp} {H:MMp} {XX} {XX}  {XX} {XXXXX} {XXXX} {XX}
  (repeated for 7 days)

  Averages:    {XXX}  {X.XX} {X.X}               {XX}  {XX}

=======================================================
  5. YESTERDAY'S ACTIVITY - {YYYY-MM-DD}
=======================================================

  Total Steps:      {XX,XXX}
  Distance:         {XX.X} km
  Active Calories:  {XXXX}
  Intensity Minutes: {XXX} (Moderate: {XX}, Vigorous: {XX})
```

## Data Sources
- `garmin.get_training_status(date)` → VO2, training status, load, balance
- `garmin.get_sleep_data(date)` → sleep timing, score, quality
- `garmin.get_heart_rates(date)` → resting HR
- `garmin.get_hrv_data(date)` → HRV last night, weekly avg
- `garmin.get_body_battery(date)` → charged/drained
- PostgreSQL `garmin_daily_metrics` → 7-day trends, yesterday's activity

## Readiness Score Weights
| Factor | Weight |
|--------|--------|
| ACWR (Load Balance) | 25% |
| Sleep | 25% |
| HRV Recovery | 20% |
| Resting HR | 15% |
| Body Battery | 15% |

## Sleep Status Tags
- `[SLEEP_STATUS:COMPLETE]` → data ready, proceed to AI Coach
- `[SLEEP_STATUS:PENDING]` → still processing, n8n retries (up to 8x, 30min apart)
- `[SLEEP_STATUS:NOT_WORN]` → watch not worn, readiness uses partial data
- `[SLEEP_STATUS:NO_DATA]` → no sleep data at all
