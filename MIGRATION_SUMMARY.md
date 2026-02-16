# Database Migration Summary - garmin_daily_metrics

## Overview
Updated `store_daily_metrics.py` to match the new optimized table schema in `create_garmin_table.sql`.

## Changes Made

### 1. Table Schema Updates

**Removed Fields (9 fields):**
- ❌ `readiness_score` - Always NULL (Garmin API doesn't return this)
- ❌ `readiness_level` - Always NULL
- ❌ `readiness_sleep_score` - Always NULL
- ❌ `readiness_sleep_history` - Always NULL
- ❌ `readiness_hrv_status` - Always NULL
- ❌ `readiness_stress_history` - Always NULL
- ❌ `readiness_acute_load` - Always NULL
- ❌ `readiness_recovery_mins` - Always NULL
- ❌ `avg_stress` - Removed (keeping only max_stress)

**Added Fields (14 fields):**

#### User Identification (1 field)
- ✅ `user_name` VARCHAR(50) DEFAULT 'Yehwan' - Support multiple family members

#### Daily Activity (7 fields)
- ✅ `total_steps` INTEGER - Daily step count
- ✅ `total_distance_km` REAL - Total distance in km
- ✅ `total_calories` INTEGER - Total calories burned
- ✅ `active_calories` INTEGER - Active calories (exercise)
- ✅ `moderate_intensity_mins` INTEGER - Minutes of moderate activity
- ✅ `vigorous_intensity_mins` INTEGER - Minutes of vigorous activity
- ✅ `floors_climbed` INTEGER - Floors climbed

#### Sleep Quality (6 fields)
- ✅ `sleep_quality` VARCHAR(20) - Quality: POOR/FAIR/GOOD/EXCELLENT
- ✅ `sleep_rem_percentage` SMALLINT - REM sleep percentage
- ✅ `sleep_light_percentage` SMALLINT - Light sleep percentage
- ✅ `sleep_deep_percentage` SMALLINT - Deep sleep percentage
- ✅ `sleep_feedback` VARCHAR(100) - Feedback (e.g., "NOT_ENOUGH_REM")
- ✅ `sleep_insight` VARCHAR(100) - Insight (e.g., "HIGHLY_STRESSFUL_DAY")

### 2. Primary Key Change
- **Before:** `PRIMARY KEY (report_date)`
- **After:** `PRIMARY KEY (user_name, report_date)`

### 3. Code Updates in store_daily_metrics.py

#### Fixed Sleep Score Bug
**Before (BROKEN - always returned NULL):**
```python
row["sleep_score"] = sleep.get("sleepScores", {}).get("overall", {}).get("value")
```

**After (FIXED):**
```python
daily_summary = sleep.get("dailySleepDTO", {})
sleep_scores = daily_summary.get("sleepScores", {})
overall_score = sleep_scores.get("overall", {})
row["sleep_score"] = overall_score.get("value")
```

#### Added Daily Activity Fetching
```python
stats = garmin.get_stats(date_str)
row["total_steps"] = stats.get("totalSteps")
row["total_distance_km"] = round(stats.get("totalDistanceMeters", 0) / 1000, 2)
row["total_calories"] = stats.get("totalKilocalories")
row["active_calories"] = stats.get("activeKilocalories")
row["moderate_intensity_mins"] = stats.get("moderateIntensityMinutes")
row["vigorous_intensity_mins"] = stats.get("vigorousIntensityMinutes")
row["floors_climbed"] = stats.get("floorsAscended")
```

#### Added Sleep Quality Fetching
```python
row["sleep_quality"] = overall_score.get("qualifierKey")
row["sleep_rem_percentage"] = sleep_scores.get("remPercentage", {}).get("value")
row["sleep_light_percentage"] = sleep_scores.get("lightPercentage", {}).get("value")
row["sleep_deep_percentage"] = sleep_scores.get("deepPercentage", {}).get("value")
row["sleep_feedback"] = daily_summary.get("sleepScoreFeedback")
row["sleep_insight"] = daily_summary.get("sleepScoreInsight")
```

### 4. Field Count Summary

| Category | Before | Removed | Added | After |
|----------|--------|---------|-------|-------|
| Identification | 1 | 0 | +1 | 2 |
| Training Load | 11 | 0 | 0 | 11 |
| Training Zones | 9 | 0 | 0 | 9 |
| HRV | 3 | 0 | 0 | 3 |
| Sleep | 8 | 0 | +6 | 14 |
| Heart Rate | 3 | 0 | 0 | 3 |
| Body Battery | 2 | 0 | 0 | 2 |
| Stress | 2 | -1 | 0 | 1 |
| Daily Activity | 0 | 0 | +7 | 7 |
| Readiness | 8 | -8 | 0 | 0 |
| Metadata | 1 | 0 | 0 | 1 |
| **TOTAL** | **48** | **-9** | **+14** | **53** |

## Testing & Backfill

### Test Today's Data
```bash
cd "/Volumes/Programming HD/Study/GraminConnector"
.venv/bin/python custom_scripts/store_daily_metrics.py
```

Expected output:
```
Connecting to Garmin...
Connected as: Yehwan Lee
Connecting to PostgreSQL...
Database ready.

Fetching metrics for 2026-02-16...
Stored: 2026-02-16 (steps=12345, acute_load=98.5, sleep=7.8h, sleep_score=65)

Done.
```

### Backfill 60 Days
```bash
.venv/bin/python custom_scripts/store_daily_metrics.py --backfill 60
```

### Backfill Full Year (365 Days)
```bash
.venv/bin/python custom_scripts/store_daily_metrics.py --backfill 365
```

## Database Connection

The script uses these environment variables from `config.py`:
- `DB_HOST` - Database host
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (should be `family_member_schedule`)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

## Next Steps

1. ✅ **Verify table exists**
   ```sql
   SELECT COUNT(*) FROM garmin_daily_metrics;
   ```

2. ✅ **Test with today's data**
   ```bash
   .venv/bin/python custom_scripts/store_daily_metrics.py
   ```

3. ✅ **Check if sleep_score is now populated**
   ```sql
   SELECT report_date, sleep_score, sleep_quality, total_steps
   FROM garmin_daily_metrics
   WHERE user_name = 'Yehwan'
   ORDER BY report_date DESC
   LIMIT 7;
   ```

4. ✅ **Backfill historical data (if needed)**
   ```bash
   .venv/bin/python custom_scripts/store_daily_metrics.py --backfill 365
   ```

5. ✅ **Update other scripts to use new fields**
   - `monthly_workload_report.py` - Add daily activity metrics
   - `daily_report.py` - Add sleep quality insights
   - `training_readiness.py` - Remove readiness fields

## Files Modified

1. ✅ `custom_scripts/store_daily_metrics.py` - Updated to new schema
2. ✅ `create_garmin_table.sql` - New optimized table schema (already created)

## Files Created

1. ✅ `create_garmin_table.sql` - Table creation script
2. ✅ `verify_table.sql` - Table verification queries
3. ✅ `setup_database.py` - Automated setup script
4. ✅ `DATABASE_SETUP_README.md` - Setup documentation
5. ✅ `MIGRATION_SUMMARY.md` - This file

---

**Migration completed:** 2026-02-16
**Status:** ✅ Ready for testing and backfill
