"""
Fetch detailed heart rate data from Garmin and store in PostgreSQL.

Runs hourly via cron. Stores ~2-min interval HR readings for the current day,
then cleans up data older than 1 month.

Usage:
    python3 custom_scripts/store_heartrate.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from garminconnect import Garmin
import garth
import psycopg2
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from config import email, password, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

SYDNEY_TZ = ZoneInfo("Australia/Sydney")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS garmin_heartrate_log (
    user_name VARCHAR(50) NOT NULL DEFAULT 'Yehwan',
    timestamp_local TIMESTAMP NOT NULL,
    heart_rate SMALLINT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT garmin_heartrate_log_pkey PRIMARY KEY (user_name, timestamp_local)
);
"""

INSERT_SQL = """
INSERT INTO garmin_heartrate_log (user_name, timestamp_local, heart_rate)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING;
"""

CLEANUP_SQL = """
DELETE FROM garmin_heartrate_log
WHERE timestamp_local < NOW() - INTERVAL '1 month';
"""


def connect_garmin():
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
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def main(target_date=None):
    today_str = target_date or date.today().isoformat()

    print(f"[store_heartrate] {datetime.now(SYDNEY_TZ).strftime('%Y-%m-%d %H:%M:%S')} — Fetching HR for {today_str}")

    # Connect
    garmin = connect_garmin()
    conn = connect_db()
    ensure_table(conn)

    # Fetch HR data
    hr_data = garmin.get_heart_rates(today_str)
    raw_pairs = hr_data.get("heartRateValues", []) if hr_data else []

    if not raw_pairs:
        print(f"  No heart rate readings found for {today_str}")
        conn.close()
        return

    # Convert epoch millis to Sydney local timestamps and insert
    rows = []
    for epoch_ms, bpm in raw_pairs:
        if bpm is None or bpm <= 0:
            continue
        dt_utc = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        dt_local = dt_utc.astimezone(SYDNEY_TZ)
        rows.append(("Yehwan", dt_local.replace(tzinfo=None), bpm))

    inserted = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(INSERT_SQL, row)
            inserted += cur.rowcount
    conn.commit()

    # Cleanup old data
    with conn.cursor() as cur:
        cur.execute(CLEANUP_SQL)
        cleaned = cur.rowcount
    conn.commit()

    # Summary
    latest_ts = rows[-1][1] if rows else None
    print(f"  Readings fetched: {len(rows)}")
    print(f"  New rows inserted: {inserted}")
    print(f"  Rows cleaned up (>1 month): {cleaned}")
    if latest_ts:
        print(f"  Latest reading: {latest_ts.strftime('%Y-%m-%d %H:%M')}")

    conn.close()
    print("  Done.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(target_date=sys.argv[1])
    else:
        main()
