"""
Fetch daily Garmin metrics and store in PostgreSQL.

Usage:
    python3 custom_scripts/store_daily_metrics.py              # store today only
    python3 custom_scripts/store_daily_metrics.py --backfill 60  # store last 60 days
"""

import sys
import os
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from garminconnect import Garmin
import garth
import psycopg2
from datetime import date, timedelta
from config import email, password, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

TRAINING_STATUS_MAP = {
    0: "NOT_APPLICABLE",
    1: "DETRAINING",
    2: "RECOVERY",
    3: "MAINTAINING",
    4: "PRODUCTIVE",
    5: "PEAKING",
    6: "OVERREACHING",
    7: "UNPRODUCTIVE",
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS garmin_daily_metrics (
    report_date         DATE PRIMARY KEY,
    -- Training Readiness
    readiness_score     SMALLINT,
    readiness_level     VARCHAR(30),
    readiness_sleep_score SMALLINT,
    readiness_sleep_history SMALLINT,
    readiness_hrv_status VARCHAR(30),
    readiness_stress_history SMALLINT,
    readiness_acute_load REAL,
    readiness_recovery_mins INTEGER,
    -- Training Status
    vo2_max             REAL,
    vo2_max_date        DATE,
    training_status     VARCHAR(30),
    training_feedback   VARCHAR(50),
    status_since        DATE,
    -- Training Load
    acute_load          REAL,
    chronic_load        REAL,
    acwr_ratio          REAL,
    acwr_status         VARCHAR(20),
    acwr_percent        SMALLINT,
    -- Monthly Load Balance
    aerobic_low         REAL,
    aerobic_low_target_min REAL,
    aerobic_low_target_max REAL,
    aerobic_high        REAL,
    aerobic_high_target_min REAL,
    aerobic_high_target_max REAL,
    anaerobic           REAL,
    anaerobic_target_min REAL,
    anaerobic_target_max REAL,
    balance_feedback    VARCHAR(50),
    -- HRV
    hrv_last_night      REAL,
    hrv_weekly_avg      REAL,
    hrv_status          VARCHAR(30),
    -- Sleep
    sleep_hours         REAL,
    sleep_score         SMALLINT,
    deep_sleep_mins     REAL,
    light_sleep_mins    REAL,
    rem_sleep_mins      REAL,
    awake_mins          REAL,
    sleep_start         TIME,
    sleep_end           TIME,
    -- Heart Rate
    resting_hr          SMALLINT,
    max_hr              SMALLINT,
    min_hr              SMALLINT,
    -- Body Battery
    body_battery_charged SMALLINT,
    body_battery_drained SMALLINT,
    -- Stress
    avg_stress          SMALLINT,
    max_stress          SMALLINT,
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW()
);
"""

UPSERT_SQL = """
INSERT INTO garmin_daily_metrics (
    report_date,
    readiness_score, readiness_level, readiness_sleep_score, readiness_sleep_history,
    readiness_hrv_status, readiness_stress_history, readiness_acute_load, readiness_recovery_mins,
    vo2_max, vo2_max_date, training_status, training_feedback, status_since,
    acute_load, chronic_load, acwr_ratio, acwr_status, acwr_percent,
    aerobic_low, aerobic_low_target_min, aerobic_low_target_max,
    aerobic_high, aerobic_high_target_min, aerobic_high_target_max,
    anaerobic, anaerobic_target_min, anaerobic_target_max, balance_feedback,
    hrv_last_night, hrv_weekly_avg, hrv_status,
    sleep_hours, sleep_score, deep_sleep_mins, light_sleep_mins,
    rem_sleep_mins, awake_mins, sleep_start, sleep_end,
    resting_hr, max_hr, min_hr,
    body_battery_charged, body_battery_drained,
    avg_stress, max_stress
) VALUES (
    %(report_date)s,
    %(readiness_score)s, %(readiness_level)s, %(readiness_sleep_score)s, %(readiness_sleep_history)s,
    %(readiness_hrv_status)s, %(readiness_stress_history)s, %(readiness_acute_load)s, %(readiness_recovery_mins)s,
    %(vo2_max)s, %(vo2_max_date)s, %(training_status)s, %(training_feedback)s, %(status_since)s,
    %(acute_load)s, %(chronic_load)s, %(acwr_ratio)s, %(acwr_status)s, %(acwr_percent)s,
    %(aerobic_low)s, %(aerobic_low_target_min)s, %(aerobic_low_target_max)s,
    %(aerobic_high)s, %(aerobic_high_target_min)s, %(aerobic_high_target_max)s,
    %(anaerobic)s, %(anaerobic_target_min)s, %(anaerobic_target_max)s, %(balance_feedback)s,
    %(hrv_last_night)s, %(hrv_weekly_avg)s, %(hrv_status)s,
    %(sleep_hours)s, %(sleep_score)s, %(deep_sleep_mins)s, %(light_sleep_mins)s,
    %(rem_sleep_mins)s, %(awake_mins)s, %(sleep_start)s, %(sleep_end)s,
    %(resting_hr)s, %(max_hr)s, %(min_hr)s,
    %(body_battery_charged)s, %(body_battery_drained)s,
    %(avg_stress)s, %(max_stress)s
)
ON CONFLICT (report_date) DO UPDATE SET
    readiness_score = EXCLUDED.readiness_score,
    readiness_level = EXCLUDED.readiness_level,
    readiness_sleep_score = EXCLUDED.readiness_sleep_score,
    readiness_sleep_history = EXCLUDED.readiness_sleep_history,
    readiness_hrv_status = EXCLUDED.readiness_hrv_status,
    readiness_stress_history = EXCLUDED.readiness_stress_history,
    readiness_acute_load = EXCLUDED.readiness_acute_load,
    readiness_recovery_mins = EXCLUDED.readiness_recovery_mins,
    vo2_max = EXCLUDED.vo2_max,
    vo2_max_date = EXCLUDED.vo2_max_date,
    training_status = EXCLUDED.training_status,
    training_feedback = EXCLUDED.training_feedback,
    status_since = EXCLUDED.status_since,
    acute_load = EXCLUDED.acute_load,
    chronic_load = EXCLUDED.chronic_load,
    acwr_ratio = EXCLUDED.acwr_ratio,
    acwr_status = EXCLUDED.acwr_status,
    acwr_percent = EXCLUDED.acwr_percent,
    aerobic_low = EXCLUDED.aerobic_low,
    aerobic_low_target_min = EXCLUDED.aerobic_low_target_min,
    aerobic_low_target_max = EXCLUDED.aerobic_low_target_max,
    aerobic_high = EXCLUDED.aerobic_high,
    aerobic_high_target_min = EXCLUDED.aerobic_high_target_min,
    aerobic_high_target_max = EXCLUDED.aerobic_high_target_max,
    anaerobic = EXCLUDED.anaerobic,
    anaerobic_target_min = EXCLUDED.anaerobic_target_min,
    anaerobic_target_max = EXCLUDED.anaerobic_target_max,
    balance_feedback = EXCLUDED.balance_feedback,
    hrv_last_night = EXCLUDED.hrv_last_night,
    hrv_weekly_avg = EXCLUDED.hrv_weekly_avg,
    hrv_status = EXCLUDED.hrv_status,
    sleep_hours = EXCLUDED.sleep_hours,
    sleep_score = EXCLUDED.sleep_score,
    deep_sleep_mins = EXCLUDED.deep_sleep_mins,
    light_sleep_mins = EXCLUDED.light_sleep_mins,
    rem_sleep_mins = EXCLUDED.rem_sleep_mins,
    awake_mins = EXCLUDED.awake_mins,
    sleep_start = EXCLUDED.sleep_start,
    sleep_end = EXCLUDED.sleep_end,
    resting_hr = EXCLUDED.resting_hr,
    max_hr = EXCLUDED.max_hr,
    min_hr = EXCLUDED.min_hr,
    body_battery_charged = EXCLUDED.body_battery_charged,
    body_battery_drained = EXCLUDED.body_battery_drained,
    avg_stress = EXCLUDED.avg_stress,
    max_stress = EXCLUDED.max_stress;
"""


def connect_garmin():
    """Connect to Garmin API and return client."""
    garth_home = os.path.expanduser("~/.garth")
    os.makedirs(garth_home, exist_ok=True)
    try:
        garth.resume(garth_home)
    except Exception:
        garth.login(email, password)
        garth.save(garth_home)
    garmin = Garmin()
    garmin.login(tokenstore=garth_home)
    return garmin


def connect_db():
    """Connect to PostgreSQL and return connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    return conn


def ensure_table(conn):
    """Create the garmin_daily_metrics table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def millis_to_time(millis):
    """Convert epoch milliseconds to a time string HH:MM for PostgreSQL TIME column."""
    if millis is None:
        return None
    from datetime import datetime
    dt = datetime.fromtimestamp(millis / 1000)
    return dt.strftime("%H:%M:%S")


def fetch_metrics(garmin, cdate):
    """Fetch all metrics for a single date and return a dict for DB insertion."""
    date_str = cdate.isoformat()
    row = {"report_date": cdate}

    # --- Training Readiness ---
    try:
        readiness = garmin.get_training_readiness(date_str)
    except Exception:
        readiness = None

    if readiness:
        row["readiness_score"] = readiness.get("score")
        row["readiness_level"] = readiness.get("levelKey", readiness.get("level"))
        row["readiness_sleep_score"] = readiness.get("sleepScore")
        row["readiness_sleep_history"] = readiness.get("sleepHistoryScore")
        row["readiness_hrv_status"] = readiness.get("hrvStatus")
        row["readiness_stress_history"] = readiness.get("stressHistoryScore")
        row["readiness_acute_load"] = readiness.get("acuteTrainingLoad")
        row["readiness_recovery_mins"] = readiness.get("recoveryTimeInMinutes")
    else:
        for k in ["readiness_score", "readiness_level", "readiness_sleep_score",
                   "readiness_sleep_history", "readiness_hrv_status",
                   "readiness_stress_history", "readiness_acute_load",
                   "readiness_recovery_mins"]:
            row[k] = None

    # --- Training Status ---
    try:
        status = garmin.get_training_status(date_str)
    except Exception:
        status = None

    if status:
        # VO2 Max
        vo2 = status.get("mostRecentVO2Max", {})
        generic = vo2.get("generic", {}) if vo2 else {}
        row["vo2_max"] = generic.get("vo2MaxPreciseValue") or generic.get("vo2MaxValue") if generic else None
        row["vo2_max_date"] = generic.get("calendarDate") if generic else None

        # Training status from latest device
        latest = status.get("mostRecentTrainingStatus", {})
        latest_data = latest.get("latestTrainingStatusData", {}) if latest else {}
        device_status = next(iter(latest_data.values()), {}) if latest_data else {}

        if device_status:
            ts_code = device_status.get("trainingStatus")
            row["training_status"] = TRAINING_STATUS_MAP.get(ts_code, str(ts_code)) if ts_code is not None else None
            row["training_feedback"] = device_status.get("trainingStatusFeedbackPhrase")
            row["status_since"] = device_status.get("sinceDate")

            # ACWR
            acwr = device_status.get("acuteTrainingLoadDTO", {})
            row["acute_load"] = acwr.get("dailyTrainingLoadAcute") if acwr else None
            row["chronic_load"] = acwr.get("dailyTrainingLoadChronic") if acwr else None
            row["acwr_ratio"] = acwr.get("dailyAcuteChronicWorkloadRatio") if acwr else None
            row["acwr_status"] = acwr.get("acwrStatus") if acwr else None
            row["acwr_percent"] = acwr.get("acwrPercent") if acwr else None
        else:
            for k in ["training_status", "training_feedback", "status_since",
                       "acute_load", "chronic_load", "acwr_ratio", "acwr_status", "acwr_percent"]:
                row[k] = None

        # Training Load Balance
        balance = status.get("mostRecentTrainingLoadBalance", {})
        balance_data = balance.get("metricsTrainingLoadBalanceDTOMap", {}) if balance else {}
        device_balance = next(iter(balance_data.values()), {}) if balance_data else {}

        if device_balance:
            row["aerobic_low"] = device_balance.get("monthlyLoadAerobicLow")
            row["aerobic_low_target_min"] = device_balance.get("monthlyLoadAerobicLowTargetMin")
            row["aerobic_low_target_max"] = device_balance.get("monthlyLoadAerobicLowTargetMax")
            row["aerobic_high"] = device_balance.get("monthlyLoadAerobicHigh")
            row["aerobic_high_target_min"] = device_balance.get("monthlyLoadAerobicHighTargetMin")
            row["aerobic_high_target_max"] = device_balance.get("monthlyLoadAerobicHighTargetMax")
            row["anaerobic"] = device_balance.get("monthlyLoadAnaerobic")
            row["anaerobic_target_min"] = device_balance.get("monthlyLoadAnaerobicTargetMin")
            row["anaerobic_target_max"] = device_balance.get("monthlyLoadAnaerobicTargetMax")
            row["balance_feedback"] = device_balance.get("trainingBalanceFeedbackPhrase")
        else:
            for k in ["aerobic_low", "aerobic_low_target_min", "aerobic_low_target_max",
                       "aerobic_high", "aerobic_high_target_min", "aerobic_high_target_max",
                       "anaerobic", "anaerobic_target_min", "anaerobic_target_max",
                       "balance_feedback"]:
                row[k] = None
    else:
        for k in ["vo2_max", "vo2_max_date", "training_status", "training_feedback",
                   "status_since", "acute_load", "chronic_load", "acwr_ratio",
                   "acwr_status", "acwr_percent",
                   "aerobic_low", "aerobic_low_target_min", "aerobic_low_target_max",
                   "aerobic_high", "aerobic_high_target_min", "aerobic_high_target_max",
                   "anaerobic", "anaerobic_target_min", "anaerobic_target_max",
                   "balance_feedback"]:
            row[k] = None

    # --- HRV ---
    try:
        hrv = garmin.get_hrv_data(date_str)
    except Exception:
        hrv = None

    if hrv:
        summary = hrv.get("hrvSummary", {})
        row["hrv_last_night"] = summary.get("lastNightAvg") if summary else None
        row["hrv_weekly_avg"] = summary.get("weeklyAvg") if summary else None
        row["hrv_status"] = summary.get("status") if summary else None
    else:
        row["hrv_last_night"] = None
        row["hrv_weekly_avg"] = None
        row["hrv_status"] = None

    # --- Sleep ---
    try:
        sleep = garmin.get_sleep_data(date_str)
    except Exception:
        sleep = None

    if sleep:
        daily_summary = sleep.get("dailySleepDTO", {})
        row["sleep_hours"] = round(daily_summary.get("sleepTimeSeconds", 0) / 3600, 2) if daily_summary.get("sleepTimeSeconds") else None
        row["sleep_score"] = sleep.get("sleepScores", {}).get("overall", {}).get("value") if sleep.get("sleepScores") else None
        row["deep_sleep_mins"] = round(daily_summary.get("deepSleepSeconds", 0) / 60, 1) if daily_summary.get("deepSleepSeconds") else None
        row["light_sleep_mins"] = round(daily_summary.get("lightSleepSeconds", 0) / 60, 1) if daily_summary.get("lightSleepSeconds") else None
        row["rem_sleep_mins"] = round(daily_summary.get("remSleepSeconds", 0) / 60, 1) if daily_summary.get("remSleepSeconds") else None
        row["awake_mins"] = round(daily_summary.get("awakeSleepSeconds", 0) / 60, 1) if daily_summary.get("awakeSleepSeconds") else None
        row["sleep_start"] = millis_to_time(daily_summary.get("sleepStartTimestampLocal"))
        row["sleep_end"] = millis_to_time(daily_summary.get("sleepEndTimestampLocal"))
    else:
        for k in ["sleep_hours", "sleep_score", "deep_sleep_mins", "light_sleep_mins",
                   "rem_sleep_mins", "awake_mins", "sleep_start", "sleep_end"]:
            row[k] = None

    # --- Heart Rate ---
    try:
        hr = garmin.get_heart_rates(date_str)
    except Exception:
        hr = None

    if hr:
        row["resting_hr"] = hr.get("restingHeartRate")
        row["max_hr"] = hr.get("maxHeartRate")
        row["min_hr"] = hr.get("minHeartRate")
    else:
        row["resting_hr"] = None
        row["max_hr"] = None
        row["min_hr"] = None

    # --- Body Battery ---
    try:
        bb = garmin.get_body_battery(date_str)
    except Exception:
        bb = None

    if bb and isinstance(bb, list) and len(bb) > 0:
        day_data = bb[0]
        row["body_battery_charged"] = day_data.get("charged")
        row["body_battery_drained"] = day_data.get("drained")
    else:
        row["body_battery_charged"] = None
        row["body_battery_drained"] = None

    # --- Stress ---
    try:
        stress = garmin.get_stress_data(date_str)
    except Exception:
        stress = None

    if stress:
        row["avg_stress"] = stress.get("overallStressLevel")
        row["max_stress"] = stress.get("maxStressLevel")
    else:
        row["avg_stress"] = None
        row["max_stress"] = None

    return row


def store_row(conn, row):
    """Upsert a single row into garmin_daily_metrics."""
    with conn.cursor() as cur:
        cur.execute(UPSERT_SQL, row)
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Store daily Garmin metrics in PostgreSQL")
    parser.add_argument("--backfill", type=int, default=0,
                        help="Number of days to backfill (e.g. 60)")
    args = parser.parse_args()

    print("Connecting to Garmin...")
    garmin = connect_garmin()
    print(f"Connected as: {garmin.get_full_name()}")

    print("Connecting to PostgreSQL...")
    conn = connect_db()
    ensure_table(conn)
    print("Database ready.")

    today = date.today()

    if args.backfill > 0:
        dates = [today - timedelta(days=i) for i in range(args.backfill)]
        dates.reverse()  # oldest first
        print(f"\nBackfilling {len(dates)} days: {dates[0]} to {dates[-1]}")
        for i, d in enumerate(dates):
            try:
                row = fetch_metrics(garmin, d)
                store_row(conn, row)
                print(f"  [{i+1}/{len(dates)}] {d} - stored (readiness={row.get('readiness_score')})")
            except Exception as e:
                print(f"  [{i+1}/{len(dates)}] {d} - ERROR: {e}")
            if i < len(dates) - 1:
                time.sleep(0.3)
    else:
        print(f"\nFetching metrics for {today}...")
        row = fetch_metrics(garmin, today)
        store_row(conn, row)
        print(f"Stored: {today} (readiness={row.get('readiness_score')}, "
              f"acute_load={row.get('acute_load')}, sleep={row.get('sleep_hours')}h)")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
