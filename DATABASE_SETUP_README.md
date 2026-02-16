# Garmin Daily Metrics - Database Setup Guide

## 📋 Overview

This setup creates an **optimized** table in the `family_member_schedule` database with:
- **53 total fields** (was 48, removed 9 useless + added 14 new)
- **Multi-user support** (user_name field for family members)
- **Enhanced sleep metrics** (quality, percentages, feedback)
- **Daily activity tracking** (steps, distance, calories, intensity)

---

## 🚀 Quick Start

### **Option 1: Run Python Setup Script (Recommended)**

```bash
cd /Volumes/Programming\ HD/Study/GraminConnector
.venv/bin/python setup_database.py
```

This will:
1. Connect to `family_member_schedule` database
2. Create the `garmin_daily_metrics` table
3. Add all indexes
4. Verify the structure
5. Show summary of new fields

### **Option 2: Run SQL Manually**

```bash
# Using psql command line
psql -h adventuretube.net -U postgres -d family_member_schedule -f create_garmin_table.sql

# Then verify
psql -h adventuretube.net -U postgres -d family_member_schedule -f verify_table.sql
```

---

## 📊 Table Structure (53 Fields)

### **1. Identification (2 fields)**
- `user_name` - VARCHAR(50) DEFAULT 'Yehwan' - **NEW**
- `report_date` - DATE (Primary key with user_name)

### **2. Training Load & Status (11 fields)**
- `training_status`, `training_feedback`, `status_since`
- `acute_load`, `chronic_load`, `acwr_ratio`, `acwr_status`, `acwr_percent`
- `vo2_max`, `vo2_max_date`, `balance_feedback`

### **3. Training Intensity Zones (9 fields)**
- `aerobic_low`, `aerobic_low_target_min`, `aerobic_low_target_max`
- `aerobic_high`, `aerobic_high_target_min`, `aerobic_high_target_max`
- `anaerobic`, `anaerobic_target_min`, `anaerobic_target_max`

### **4. HRV (3 fields)**
- `hrv_last_night`, `hrv_weekly_avg`, `hrv_status`

### **5. Sleep - ENHANCED (13 fields)**
- Basic: `sleep_hours`, `deep_sleep_mins`, `light_sleep_mins`, `rem_sleep_mins`, `awake_mins`
- Timing: `sleep_start`, `sleep_end`
- **NEW Quality Metrics**:
  - `sleep_score` - Overall score 0-100
  - `sleep_quality` - POOR/FAIR/GOOD/EXCELLENT **NEW**
  - `sleep_rem_percentage` - REM % **NEW**
  - `sleep_light_percentage` - Light % **NEW**
  - `sleep_deep_percentage` - Deep % **NEW**
  - `sleep_feedback` - Feedback text **NEW**
  - `sleep_insight` - Insight text **NEW**

### **6. Heart Rate (3 fields)**
- `resting_hr`, `max_hr`, `min_hr`

### **7. Body Battery & Stress (3 fields)**
- `body_battery_charged`, `body_battery_drained`, `max_stress`

### **8. Daily Activity - NEW (7 fields)**
- `total_steps` - Daily step count **NEW**
- `total_distance_km` - Distance in km **NEW**
- `total_calories` - Total calories **NEW**
- `active_calories` - Active calories **NEW**
- `moderate_intensity_mins` - Moderate intensity **NEW**
- `vigorous_intensity_mins` - Vigorous intensity **NEW**
- `floors_climbed` - Floors climbed **NEW**

### **9. Metadata (1 field)**
- `created_at` - Timestamp

---

## 🗑️ Fields Removed (9 total)

These fields were **always NULL** in the old schema:
- `readiness_score`
- `readiness_level`
- `readiness_sleep_score`
- `readiness_sleep_history`
- `readiness_hrv_status`
- `readiness_stress_history`
- `readiness_acute_load`
- `readiness_recovery_mins`
- `avg_stress`

**Reason**: Garmin API doesn't provide this data (always returned NULL).

---

## 🔍 Verification

After creating the table, verify it:

```bash
.venv/bin/python -c "
import psycopg2

conn = psycopg2.connect(
    host='adventuretube.net',
    port=5432,
    database='family_member_schedule',
    user='postgres',
    password='5785Ch00'
)

cursor = conn.cursor()

# Check column count
cursor.execute('''
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_name = 'garmin_daily_metrics'
''')
print(f'Total columns: {cursor.fetchone()[0]}')

# Check primary key
cursor.execute('''
    SELECT constraint_name FROM information_schema.table_constraints
    WHERE table_name = 'garmin_daily_metrics' AND constraint_type = 'PRIMARY KEY'
''')
print(f'Primary key: {cursor.fetchone()[0]}')

conn.close()
print('✅ Table verified!')
"
```

Expected output:
```
Total columns: 53
Primary key: garmin_daily_metrics_pkey
✅ Table verified!
```

---

## 📝 Next Steps

After creating the table:

### **1. Update `store_daily_metrics.py`**

Need to modify the script to:
- Connect to `family_member_schedule` database (not `adventuretube`)
- Fetch new fields from `get_stats()` API (steps, distance, calories)
- Fix sleep_score path: `dailySleepDTO.sleepScores.overall.value`
- Add new sleep quality fields
- Include `user_name = 'Yehwan'` in INSERT

### **2. Backfill Historical Data**

Run the updated script for all past dates to populate:
- Steps, distance, calories for all 365 days
- Sleep quality metrics for days with sleep data
- User name for all existing records

### **3. Update Reports**

Modify reporting scripts to show:
- Daily step counts
- Total distance on high-load days
- Sleep quality trends
- Intensity minutes compliance

---

## 🎯 What This Enables

With the new fields, you can now:

1. ✅ "How many steps on the 1,719 peak workload day?"
2. ✅ "Total distance walked in March 2025?"
3. ✅ "Average sleep quality in peak training month?"
4. ✅ "REM sleep percentage trends over time?"
5. ✅ "Calories burned on 500+ load days?"
6. ✅ "WHO intensity minutes compliance (150+/week)?"
7. ✅ "Compare Yehwan's metrics with other family members"

---

## 📞 Database Connection Info

```python
DB_CONFIG = {
    'host': 'adventuretube.net',
    'port': 5432,
    'database': 'family_member_schedule',  # Changed from 'adventuretube'
    'user': 'postgres',
    'password': '5785Ch00'
}
```

---

## ⚠️ Important Notes

1. **This creates a NEW table** - Old data in `adventuretube` database is not affected
2. **Primary key is composite**: (user_name, report_date) for multi-user support
3. **Sleep score path fixed**: Now correctly fetches from `dailySleepDTO.sleepScores`
4. **14 new fields added**: 1 user + 7 activity + 6 sleep quality
5. **9 useless fields removed**: All the always-NULL readiness fields

---

## 🔗 Files Created

- `create_garmin_table.sql` - Complete table creation SQL
- `verify_table.sql` - Verification queries
- `setup_database.py` - Python setup script (recommended)
- `DATABASE_SETUP_README.md` - This file

---

**Ready to create the table? Run `setup_database.py`!**
