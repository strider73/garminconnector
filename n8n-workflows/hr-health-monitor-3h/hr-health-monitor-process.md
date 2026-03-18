# HR Health Monitor 3H — Process

## Trigger
Every 3 hours

## Pipeline

### Step 1: Collect HR Data (cron job on server, not n8n)
- `store_heartrate.py` runs hourly via cron on the server
- Connects to Garmin API via `garth` OAuth
- Fetches today's heart rate readings (~2-min intervals, ~435 readings/day)
- Inserts new readings into PostgreSQL `garmin_heartrate_log` table
- Cleans up data older than 1 month

### Step 2: Health Check (n8n SSH node)
- n8n queries PostgreSQL directly (no Python script):
  ```sql
  SELECT MAX(timestamp_local), COUNT(*)
  FROM garmin_heartrate_log
  WHERE user_name = 'Yehwan'
  AND timestamp_local > NOW() - INTERVAL '3 hours'
  ```
- Checks if any HR readings exist in the last 3 hours

### Step 3: Alert or Pass (n8n If node)
- **Has data** → All Good (no action)
- **No data** → Alert via Telegram to both Chris and Yehwan:
  "No heart rate data in the last 3 hours — watch not worn, cron failed, or API issue"

## No AI Coach
This workflow monitors data collection health — no coaching output.

## Files Used
- `n8n-workflows/hr-health-monitor-3h/store_heartrate.py` (runs via cron, not n8n directly)
