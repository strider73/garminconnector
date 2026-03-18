# Store Daily Metrics 9pm — Process

## Trigger
Every day at 9:00pm AEST

## Pipeline

### Step 1: Run Python Script (`store_daily_metrics.py`)
- Connects to Garmin API via `garth` OAuth
- Fetches today's full metrics:
  - Training load: acute load, chronic load, ACWR, training status
  - HRV: last night, weekly average, status
  - Sleep: duration, stages, scores, quality, percentages
  - Heart rate: resting, max, min
  - Body battery: charged, drained
  - Stress: max stress
  - Activity: steps, distance, calories, intensity minutes, floors
- Upserts all data into PostgreSQL `garmin_daily_metrics` table
- Outputs confirmation with key values to stdout

### Step 2: Update Baselines (`update_baselines.py` via Claude Agent)
- Queries PostgreSQL for all historical data
- Recalculates baseline statistics (means, standard deviations, ranges)
- Regenerates `.claude/reference/YEHWAN-profile.md` from template
- Regenerates `.claude/reference/YEHWAN-training-intensity-index.md` from template
- This ensures the AI coaching commands always use up-to-date baselines

## No AI Coach
This workflow stores data only — no coaching output, no email/Telegram delivery.

## Files Used
- `n8n-workflows/store-daily-metrics-9pm/store_daily_metrics.py`
- `.claude/agents/scripts/update_baselines.py`
- `.claude/agents/update-baselines.md`
- `.claude/templates/YEHWAN-profile.template.md`
- `.claude/templates/YEHWAN-training-intensity-index.template.md`
- `.claude/reference/YEHWAN-profile.md` (output)
- `.claude/reference/YEHWAN-training-intensity-index.md` (output)
