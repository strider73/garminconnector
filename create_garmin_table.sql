-- ============================================================================
-- Garmin Daily Metrics Table - Optimized Schema
-- Database: family_member_schedule
-- Table: garmin_daily_metrics
-- Purpose: Store daily health and training metrics from Garmin Connect
-- ============================================================================

-- Drop table if exists (WARNING: This will delete all data!)
-- DROP TABLE IF EXISTS garmin_daily_metrics;

CREATE TABLE IF NOT EXISTS garmin_daily_metrics (
    -- ========================================================================
    -- 1. IDENTIFICATION (2 fields)
    -- ========================================================================
    user_name VARCHAR(50) NOT NULL DEFAULT 'Yehwan',
    report_date DATE NOT NULL,

    -- ========================================================================
    -- 2. TRAINING LOAD & STATUS (11 fields)
    -- ========================================================================
    training_status VARCHAR(50),
    training_feedback VARCHAR(100),
    status_since DATE,
    acute_load REAL,
    chronic_load REAL,
    acwr_ratio REAL,
    acwr_status VARCHAR(20),
    acwr_percent SMALLINT,
    vo2_max REAL,
    vo2_max_date DATE,
    balance_feedback VARCHAR(100),

    -- ========================================================================
    -- 3. TRAINING INTENSITY ZONES (9 fields)
    -- ========================================================================
    aerobic_low REAL,
    aerobic_low_target_min REAL,
    aerobic_low_target_max REAL,
    aerobic_high REAL,
    aerobic_high_target_min REAL,
    aerobic_high_target_max REAL,
    anaerobic REAL,
    anaerobic_target_min REAL,
    anaerobic_target_max REAL,

    -- ========================================================================
    -- 4. HRV - Heart Rate Variability (3 fields)
    -- ========================================================================
    hrv_last_night REAL,
    hrv_weekly_avg REAL,
    hrv_status VARCHAR(20),

    -- ========================================================================
    -- 5. SLEEP (13 fields) - ENHANCED with quality metrics
    -- ========================================================================
    sleep_hours REAL,
    sleep_score SMALLINT,
    sleep_quality VARCHAR(20),
    sleep_rem_percentage SMALLINT,
    sleep_light_percentage SMALLINT,
    sleep_deep_percentage SMALLINT,
    sleep_feedback VARCHAR(100),
    sleep_insight VARCHAR(100),
    deep_sleep_mins REAL,
    light_sleep_mins REAL,
    rem_sleep_mins REAL,
    awake_mins REAL,
    sleep_start TIME,
    sleep_end TIME,

    -- ========================================================================
    -- 6. HEART RATE (3 fields)
    -- ========================================================================
    resting_hr SMALLINT,
    max_hr SMALLINT,
    min_hr SMALLINT,

    -- ========================================================================
    -- 7. BODY BATTERY & STRESS (3 fields)
    -- ========================================================================
    body_battery_charged SMALLINT,
    body_battery_drained SMALLINT,
    max_stress SMALLINT,

    -- ========================================================================
    -- 8. DAILY ACTIVITY (7 fields) - NEW
    -- ========================================================================
    total_steps INTEGER,
    total_distance_km REAL,
    total_calories INTEGER,
    active_calories INTEGER,
    moderate_intensity_mins INTEGER,
    vigorous_intensity_mins INTEGER,
    floors_climbed INTEGER,

    -- ========================================================================
    -- 9. METADATA (1 field)
    -- ========================================================================
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- ========================================================================
    -- PRIMARY KEY
    -- ========================================================================
    CONSTRAINT garmin_daily_metrics_pkey PRIMARY KEY (user_name, report_date)
);

-- ============================================================================
-- INDEXES for better query performance
-- ============================================================================

-- Index on report_date for date range queries
CREATE INDEX IF NOT EXISTS idx_garmin_report_date
ON garmin_daily_metrics(report_date DESC);

-- Index on user_name for multi-user queries
CREATE INDEX IF NOT EXISTS idx_garmin_user_name
ON garmin_daily_metrics(user_name);

-- Index on acute_load for workload queries
CREATE INDEX IF NOT EXISTS idx_garmin_acute_load
ON garmin_daily_metrics(acute_load DESC) WHERE acute_load IS NOT NULL;

-- Index on sleep_score for sleep quality queries
CREATE INDEX IF NOT EXISTS idx_garmin_sleep_score
ON garmin_daily_metrics(sleep_score DESC) WHERE sleep_score IS NOT NULL;

-- Composite index for user + date range queries
CREATE INDEX IF NOT EXISTS idx_garmin_user_date
ON garmin_daily_metrics(user_name, report_date DESC);

-- ============================================================================
-- COMMENTS for documentation
-- ============================================================================

COMMENT ON TABLE garmin_daily_metrics IS 'Daily health and training metrics from Garmin Connect API';

COMMENT ON COLUMN garmin_daily_metrics.user_name IS 'User identifier - default Yehwan, supports multiple family members';
COMMENT ON COLUMN garmin_daily_metrics.report_date IS 'Date of the metrics report';
COMMENT ON COLUMN garmin_daily_metrics.acute_load IS '7-day training load average';
COMMENT ON COLUMN garmin_daily_metrics.chronic_load IS '28-day training load average';
COMMENT ON COLUMN garmin_daily_metrics.acwr_ratio IS 'Acute:Chronic Workload Ratio - injury risk indicator';
COMMENT ON COLUMN garmin_daily_metrics.sleep_score IS 'Overall sleep score 0-100 from Garmin';
COMMENT ON COLUMN garmin_daily_metrics.sleep_quality IS 'Sleep quality: POOR, FAIR, GOOD, EXCELLENT';
COMMENT ON COLUMN garmin_daily_metrics.total_steps IS 'Total daily step count';
COMMENT ON COLUMN garmin_daily_metrics.total_distance_km IS 'Total distance covered in kilometers';

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================================================

-- Grant permissions to postgres user (already owner)
-- GRANT ALL PRIVILEGES ON garmin_daily_metrics TO postgres;

-- ============================================================================
-- TABLE SUMMARY
-- ============================================================================
-- Total Fields: 53
--   - Identification: 2
--   - Training Load & Status: 11
--   - Training Intensity Zones: 9
--   - HRV: 3
--   - Sleep: 13 (enhanced with quality metrics)
--   - Heart Rate: 3
--   - Body Battery & Stress: 3
--   - Daily Activity: 7 (NEW)
--   - Metadata: 1
--
-- Optimizations:
--   - Removed 9 always-NULL readiness fields
--   - Added 7 daily activity fields (steps, distance, calories, etc.)
--   - Added 6 sleep quality fields (quality, percentages, feedback)
--   - Added user_name for multi-user support
--   - Added indexes for common query patterns
--
-- Database: family_member_schedule
-- Connection: adventuretube.net:5432
-- ============================================================================
