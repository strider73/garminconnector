-- ============================================================================
-- Table Verification Script
-- Run this after creating the table to verify structure
-- ============================================================================

-- Check if table exists
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE tablename = 'garmin_daily_metrics';

-- Get total column count
SELECT COUNT(*) as total_columns
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics';

-- List all columns with their data types
SELECT
    ordinal_position as "#",
    column_name,
    data_type,
    character_maximum_length as max_length,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
ORDER BY ordinal_position;

-- Check primary key
SELECT
    conname as constraint_name,
    pg_get_constraintdef(c.oid) as constraint_definition
FROM pg_constraint c
JOIN pg_namespace n ON n.oid = c.connamespace
WHERE contype = 'p'
AND conrelid = 'garmin_daily_metrics'::regclass;

-- Check indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'garmin_daily_metrics'
ORDER BY indexname;

-- Get table size (will be 0 if empty)
SELECT
    pg_size_pretty(pg_total_relation_size('garmin_daily_metrics')) as table_size,
    pg_size_pretty(pg_relation_size('garmin_daily_metrics')) as data_size,
    pg_size_pretty(pg_total_relation_size('garmin_daily_metrics') - pg_relation_size('garmin_daily_metrics')) as index_size;

-- Column count by category (manual verification)
SELECT
    '1. Identification' as category,
    COUNT(*) as field_count
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('user_name', 'report_date')

UNION ALL

SELECT
    '2. Training Load & Status',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('training_status', 'training_feedback', 'status_since',
                     'acute_load', 'chronic_load', 'acwr_ratio', 'acwr_status',
                     'acwr_percent', 'vo2_max', 'vo2_max_date', 'balance_feedback')

UNION ALL

SELECT
    '3. Training Intensity Zones',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('aerobic_low', 'aerobic_low_target_min', 'aerobic_low_target_max',
                     'aerobic_high', 'aerobic_high_target_min', 'aerobic_high_target_max',
                     'anaerobic', 'anaerobic_target_min', 'anaerobic_target_max')

UNION ALL

SELECT
    '4. HRV',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('hrv_last_night', 'hrv_weekly_avg', 'hrv_status')

UNION ALL

SELECT
    '5. Sleep (ENHANCED)',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('sleep_hours', 'sleep_score', 'sleep_quality',
                     'sleep_rem_percentage', 'sleep_light_percentage', 'sleep_deep_percentage',
                     'sleep_feedback', 'sleep_insight',
                     'deep_sleep_mins', 'light_sleep_mins', 'rem_sleep_mins', 'awake_mins',
                     'sleep_start', 'sleep_end')

UNION ALL

SELECT
    '6. Heart Rate',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('resting_hr', 'max_hr', 'min_hr')

UNION ALL

SELECT
    '7. Body Battery & Stress',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('body_battery_charged', 'body_battery_drained', 'max_stress')

UNION ALL

SELECT
    '8. Daily Activity (NEW)',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('total_steps', 'total_distance_km', 'total_calories',
                     'active_calories', 'moderate_intensity_mins',
                     'vigorous_intensity_mins', 'floors_climbed')

UNION ALL

SELECT
    '9. Metadata',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'
AND column_name IN ('created_at')

UNION ALL

SELECT
    'TOTAL',
    COUNT(*)
FROM information_schema.columns
WHERE table_name = 'garmin_daily_metrics'

ORDER BY category;

-- ============================================================================
-- Expected Results:
-- ============================================================================
-- 1. Identification: 2
-- 2. Training Load & Status: 11
-- 3. Training Intensity Zones: 9
-- 4. HRV: 3
-- 5. Sleep (ENHANCED): 13
-- 6. Heart Rate: 3
-- 7. Body Battery & Stress: 3
-- 8. Daily Activity (NEW): 7
-- 9. Metadata: 1
-- TOTAL: 53
-- ============================================================================
