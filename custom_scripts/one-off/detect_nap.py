"""
Detect nap periods from heart rate data using rolling average + variability.

Algorithm:
  1. Query DB for daytime HR data (from wake-up onward)
  2. Compute rolling avg HR and rolling std dev (20-min window)
  3. Nap = sustained period where rolling avg < threshold AND std dev < threshold
  4. Minimum 20 minutes duration

Usage:
    python3 custom_scripts/detect_nap.py              # today
    python3 custom_scripts/detect_nap.py 2026-03-04   # specific date
"""

import sys
import os
import statistics
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# --- Config ---
RESTING_HR = 50          # Yehwan's resting HR
NAP_HR_THRESHOLD = 70    # rolling avg must be below this
NAP_STD_THRESHOLD = 6    # rolling std must be below this (stable/flat pattern)
WINDOW_SIZE = 10          # 10 readings = ~20 min (2-min intervals)
MIN_NAP_MINUTES = 20      # minimum nap duration
DAYTIME_START_HOUR = 11   # ignore before 11 AM (morning sitting = false positives)
DAYTIME_END_HOUR = 21     # ignore after 9 PM (nighttime sleep)


def connect_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
    )


def fetch_daytime_hr(conn, target_date):
    """Fetch HR data for daytime hours on target date."""
    sql = """
        SELECT timestamp_local, heart_rate
        FROM garmin_heartrate_log
        WHERE user_name = 'Yehwan'
          AND timestamp_local::date = %s
          AND EXTRACT(HOUR FROM timestamp_local) >= %s
          AND EXTRACT(HOUR FROM timestamp_local) < %s
        ORDER BY timestamp_local
    """
    with conn.cursor() as cur:
        cur.execute(sql, (target_date, DAYTIME_START_HOUR, DAYTIME_END_HOUR))
        return cur.fetchall()


def compute_rolling(hrs, window):
    """Compute trailing rolling average and std deviation (no look-ahead)."""
    rolling_avg = []
    rolling_std = []
    for i in range(len(hrs)):
        start = max(0, i - window + 1)
        w = hrs[start:i + 1]
        rolling_avg.append(statistics.mean(w))
        rolling_std.append(statistics.stdev(w) if len(w) > 1 else 0)
    return rolling_avg, rolling_std


def detect_naps(times, hrs, rolling_avg, rolling_std):
    """Find nap periods where both rolling avg and std are below thresholds."""
    naps = []
    in_nap = False
    nap_start_idx = None

    for i in range(len(times)):
        # Entry: need BOTH low avg AND low std (confirmed sleep pattern)
        is_nap_entry = rolling_avg[i] < NAP_HR_THRESHOLD and rolling_std[i] < NAP_STD_THRESHOLD
        # Exit: std dev spikes (HR gets bouncy = woke up) — this is the primary wake signal
        is_wake_up = rolling_std[i] > NAP_STD_THRESHOLD * 1.5

        if is_nap_entry and not in_nap:
            in_nap = True
            nap_start_idx = i
        elif is_wake_up and in_nap:
            in_nap = False
            duration = (times[i - 1] - times[nap_start_idx]).total_seconds() / 60
            if duration >= MIN_NAP_MINUTES:
                nap_hrs = hrs[nap_start_idx:i]
                naps.append({
                    'start': times[nap_start_idx],
                    'end': times[i - 1],
                    'duration_min': round(duration),
                    'avg_hr': round(statistics.mean(nap_hrs)),
                    'min_hr': min(nap_hrs),
                    'std_hr': round(statistics.stdev(nap_hrs), 1) if len(nap_hrs) > 1 else 0,
                })

    # Handle nap still in progress at end of data
    if in_nap:
        duration = (times[-1] - times[nap_start_idx]).total_seconds() / 60
        if duration >= MIN_NAP_MINUTES:
            nap_hrs = hrs[nap_start_idx:]
            naps.append({
                'start': times[nap_start_idx],
                'end': times[-1],
                'duration_min': round(duration),
                'avg_hr': round(statistics.mean(nap_hrs)),
                'min_hr': min(nap_hrs),
                'std_hr': round(statistics.stdev(nap_hrs), 1) if len(nap_hrs) > 1 else 0,
            })

    return naps


def main(target_date=None):
    target = target_date or date.today().isoformat()

    conn = connect_db()
    rows = fetch_daytime_hr(conn, target)
    conn.close()

    if not rows:
        print(f"No HR data for {target}")
        return []

    times = [r[0] for r in rows]
    hrs = [r[1] for r in rows]

    print(f"[detect_nap] {target} — {len(rows)} readings ({times[0].strftime('%I:%M %p')} - {times[-1].strftime('%I:%M %p')})")
    print(f"  Day avg HR: {round(statistics.mean(hrs))} bpm | Min: {min(hrs)} | Max: {max(hrs)}")

    rolling_avg, rolling_std = compute_rolling(hrs, WINDOW_SIZE)
    naps = detect_naps(times, hrs, rolling_avg, rolling_std)

    # Filter: nap avg HR must be well below day median (not just morning grogginess)
    day_median = statistics.median(hrs)
    naps = [n for n in naps if n['avg_hr'] < day_median - 10]

    if naps:
        print(f"\n  NAP DETECTED ({len(naps)}):")
        for n in naps:
            print(f"    {n['start'].strftime('%I:%M %p')} → {n['end'].strftime('%I:%M %p')} ({n['duration_min']} min)")
            print(f"    Avg HR: {n['avg_hr']} bpm | Min: {n['min_hr']} | Std: {n['std_hr']}")
    else:
        print("\n  No nap detected.")

    return naps


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(target_date=sys.argv[1])
    else:
        main()
