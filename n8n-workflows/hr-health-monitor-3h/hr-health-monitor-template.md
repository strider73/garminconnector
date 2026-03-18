# HR Health Monitor Output Template

## store_heartrate.py (runs hourly via cron)

```
Connecting to Garmin...
Connected as: {full_name}

Fetching heart rate data for {YYYY-MM-DD}...
  Readings fetched: {XXX}
  New rows inserted: {XX}
  Rows cleaned up (>1 month): {XX}
  Latest reading: {YYYY-MM-DD HH:MM}
  Done.
```

## What Gets Stored (PostgreSQL `garmin_heartrate_log` table)

| Field | Type | Description |
|-------|------|-------------|
| user_name | VARCHAR(50) | Default 'Yehwan' |
| timestamp_local | TIMESTAMP | Local time of reading |
| heart_rate | SMALLINT | HR value in bpm |
| created_at | TIMESTAMP | When row was inserted |

- ~435 readings per day (~2-min intervals)
- Automatically cleans up data older than 1 month
- Upserts to avoid duplicates

## n8n Health Check (every 3 hours)

The n8n workflow does NOT run the Python script — it queries PostgreSQL directly:

```sql
SELECT COALESCE(MAX(timestamp_local)::text, 'NONE') as last_reading,
       COUNT(*) as readings_recent
FROM garmin_heartrate_log
WHERE user_name = 'Yehwan'
  AND timestamp_local > (NOW() AT TIME ZONE 'Australia/Sydney') - INTERVAL '3 hours';
```

### Alert Message (sent when no data found)

```
⚠️ No heart rate data in the last 3 hours for Yehwan.

Possible causes:
• Watch not being worn
• Cron job failed
• Garmin API issue

— GarminConnector Health Monitor
```

## Data Source (Garmin API)
- `garmin.get_heart_rates(date)` → heartRateValues array (timestamp + HR pairs)
