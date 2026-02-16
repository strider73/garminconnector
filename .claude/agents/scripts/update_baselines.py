"""
Recalculate Yehwan's training baselines from PostgreSQL and regenerate
YEHWAN-profile.md and YEHWAN-training-intensity-index.md from templates.

Usage:
    python3 .claude/agents/scripts/update_baselines.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, ".claude", "templates")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, ".claude")

PROFILE_TEMPLATE = os.path.join(TEMPLATE_DIR, "YEHWAN-profile.template.md")
PROFILE_OUTPUT = os.path.join(OUTPUT_DIR, "YEHWAN-profile.md")
INTENSITY_TEMPLATE = os.path.join(TEMPLATE_DIR, "YEHWAN-training-intensity-index.template.md")
INTENSITY_OUTPUT = os.path.join(OUTPUT_DIR, "YEHWAN-training-intensity-index.md")


def connect_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
    )


def query_one(cur, sql):
    """Execute query and return single row as dict."""
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    return dict(zip(cols, row)) if row else {}


def query_all(cur, sql):
    """Execute query and return all rows as list of dicts."""
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def fmt(val, decimals=1):
    """Format a numeric value with specified decimals, or '?' if None."""
    if val is None:
        return "?"
    return f"{float(val):.{decimals}f}"


def fmt_int(val):
    """Format as integer, or '?' if None."""
    if val is None:
        return "?"
    return str(int(round(float(val))))


def fmt_comma(val):
    """Format integer with comma separators (e.g. 8,751)."""
    if val is None:
        return "?"
    return f"{int(round(float(val))):,}"


def format_date_short(d):
    """Format date as 'Mar 6, 2025'."""
    if d is None:
        return "?"
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[d.month - 1]} {d.day}, {d.year}"


def format_date_long(d):
    """Format date as 'March 6, 2025'."""
    if d is None:
        return "?"
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return f"{months[d.month - 1]} {d.day}, {d.year}"


def calculate_thresholds(mean, std):
    """Calculate alert thresholds from mean ± std for metrics where HIGH is bad (RHR).
    Returns (normal_lo, normal_hi, warning, alert) all as ints.
    """
    if mean is None or std is None:
        return ("?", "?", "?", "?")
    m, s = float(mean), float(std)
    return (
        int(round(m - s)),
        int(round(m + s)),
        int(round(m + 1.5 * s)),
        int(round(m + 2 * s)),
    )


def calculate_thresholds_inverted(mean, std):
    """For metrics where LOW is bad (HRV, sleep score).
    Warning/alert are below the mean.
    """
    if mean is None or std is None:
        return ("?", "?", "?", "?")
    m, s = float(mean), float(std)
    return (
        int(round(m - s)),
        int(round(m + s)),
        int(round(m - 1.5 * s)),
        int(round(m - 2 * s)),
    )


def main():
    print("Connecting to PostgreSQL...")
    conn = connect_db()
    cur = conn.cursor()
    print(f"Connected to {DB_NAME}.")

    # ── Date range ──
    date_range = query_one(cur, """
        SELECT
            MIN(report_date) as first_date,
            MAX(report_date) as last_date,
            COUNT(*) as total_days,
            COUNT(hrv_last_night) as watch_worn_days,
            COUNT(active_calories) as activity_days
        FROM garmin_daily_metrics
    """)
    print(f"Date range: {date_range['first_date']} to {date_range['last_date']} "
          f"({date_range['total_days']} days, {date_range['watch_worn_days']} watch-worn, "
          f"{date_range['activity_days']} with activity data)")

    # ── Recovery baselines (watch-worn days) ──
    recovery = query_one(cur, """
        SELECT
            ROUND(AVG(resting_hr)::numeric, 1) as rhr_mean,
            ROUND(STDDEV(resting_hr)::numeric, 1) as rhr_std,
            MIN(resting_hr) as rhr_min,
            MAX(resting_hr) as rhr_max,
            ROUND(AVG(hrv_last_night)::numeric, 1) as hrv_mean,
            ROUND(STDDEV(hrv_last_night)::numeric, 1) as hrv_std,
            MIN(hrv_last_night)::int as hrv_min,
            MAX(hrv_last_night)::int as hrv_max,
            ROUND(AVG(hrv_weekly_avg)::numeric, 1) as hrv_wk_mean,
            ROUND(STDDEV(hrv_weekly_avg)::numeric, 1) as hrv_wk_std,
            MIN(hrv_weekly_avg)::int as hrv_wk_min,
            MAX(hrv_weekly_avg)::int as hrv_wk_max,
            ROUND(AVG(vo2_max)::numeric, 1) as vo2_mean,
            ROUND(STDDEV(vo2_max)::numeric, 1) as vo2_std,
            MIN(vo2_max)::int as vo2_min,
            MAX(vo2_max)::int as vo2_max_val
        FROM garmin_daily_metrics
        WHERE hrv_last_night IS NOT NULL
    """)
    print(f"Recovery: RHR={recovery['rhr_mean']}±{recovery['rhr_std']}, "
          f"HRV={recovery['hrv_mean']}±{recovery['hrv_std']}, "
          f"VO2={recovery['vo2_mean']}±{recovery['vo2_std']}")

    # ── Sleep baselines ──
    sleep = query_one(cur, """
        SELECT
            ROUND(AVG(sleep_hours)::numeric, 1) as sleep_hrs_mean,
            ROUND(STDDEV(sleep_hours)::numeric, 1) as sleep_hrs_std,
            MIN(sleep_hours)::int as sleep_hrs_min,
            MAX(sleep_hours)::int as sleep_hrs_max,
            ROUND(AVG(sleep_score)::numeric, 1) as sleep_score_mean,
            ROUND(STDDEV(sleep_score)::numeric, 1) as sleep_score_std,
            MIN(sleep_score) as sleep_score_min,
            MAX(sleep_score) as sleep_score_max,
            ROUND(AVG(CASE WHEN sleep_hours > 0 THEN deep_sleep_mins / (sleep_hours * 60) * 100 END)::numeric, 1) as deep_pct_mean,
            ROUND(STDDEV(CASE WHEN sleep_hours > 0 THEN deep_sleep_mins / (sleep_hours * 60) * 100 END)::numeric, 1) as deep_pct_std,
            MIN(CASE WHEN sleep_hours > 0 THEN ROUND((deep_sleep_mins / (sleep_hours * 60) * 100)::numeric, 0) END)::int as deep_pct_min,
            MAX(CASE WHEN sleep_hours > 0 THEN ROUND((deep_sleep_mins / (sleep_hours * 60) * 100)::numeric, 0) END)::int as deep_pct_max,
            ROUND(AVG(CASE WHEN sleep_hours > 0 THEN rem_sleep_mins / (sleep_hours * 60) * 100 END)::numeric, 1) as rem_pct_mean,
            ROUND(STDDEV(CASE WHEN sleep_hours > 0 THEN rem_sleep_mins / (sleep_hours * 60) * 100 END)::numeric, 1) as rem_pct_std,
            MIN(CASE WHEN sleep_hours > 0 THEN ROUND((rem_sleep_mins / (sleep_hours * 60) * 100)::numeric, 0) END)::int as rem_pct_min,
            MAX(CASE WHEN sleep_hours > 0 THEN ROUND((rem_sleep_mins / (sleep_hours * 60) * 100)::numeric, 0) END)::int as rem_pct_max
        FROM garmin_daily_metrics
        WHERE sleep_hours IS NOT NULL AND sleep_hours > 0
    """)
    print(f"Sleep: {sleep['sleep_hrs_mean']}±{sleep['sleep_hrs_std']}h, "
          f"score={sleep['sleep_score_mean']}±{sleep['sleep_score_std']}")

    # ── Activity baselines ──
    activity = query_one(cur, """
        SELECT
            ROUND(AVG(total_steps)::numeric, 0)::int as steps_mean,
            ROUND(STDDEV(total_steps)::numeric, 0)::int as steps_std,
            MIN(total_steps) as steps_min,
            MAX(total_steps) as steps_max,
            ROUND(AVG(total_distance_km)::numeric, 1) as dist_mean,
            ROUND(STDDEV(total_distance_km)::numeric, 1) as dist_std,
            MIN(total_distance_km)::int as dist_min,
            MAX(total_distance_km)::int as dist_max,
            ROUND(AVG(active_calories)::numeric, 0)::int as acal_mean,
            ROUND(STDDEV(active_calories)::numeric, 0)::int as acal_std,
            MIN(active_calories) as acal_min,
            MAX(active_calories) as acal_max,
            ROUND(AVG(moderate_intensity_mins)::numeric, 1) as mod_mins_mean,
            ROUND(STDDEV(moderate_intensity_mins)::numeric, 1) as mod_mins_std,
            ROUND(AVG(vigorous_intensity_mins)::numeric, 1) as vig_mins_mean,
            ROUND(STDDEV(vigorous_intensity_mins)::numeric, 1) as vig_mins_std
        FROM garmin_daily_metrics
        WHERE active_calories IS NOT NULL
    """)
    print(f"Activity: steps={activity['steps_mean']}±{activity['steps_std']}, "
          f"active_cal={activity['acal_mean']}±{activity['acal_std']}")

    # ── Intensity distribution ──
    intensity_rows = query_all(cur, """
        SELECT
            CASE
                WHEN active_calories < 300 THEN 'Rest/Recovery'
                WHEN active_calories < 600 THEN 'Light Training'
                WHEN active_calories < 1000 THEN 'Moderate Training'
                WHEN active_calories < 1500 THEN 'Hard Training'
                ELSE 'Very Hard Training'
            END as intensity,
            COUNT(*) as days,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct,
            ROUND(AVG(acute_load)::numeric, 0)::int as avg_acute,
            MIN(acute_load)::int as min_acute,
            MAX(acute_load)::int as max_acute
        FROM garmin_daily_metrics
        WHERE active_calories IS NOT NULL
        GROUP BY 1
        ORDER BY MIN(active_calories)
    """)
    intensity = {row["intensity"]: row for row in intensity_rows}

    load_thresholds = query_one(cur, """
        SELECT
            ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY active_calories)::numeric, 0)::int as p90_cal
        FROM garmin_daily_metrics
        WHERE active_calories IS NOT NULL
    """)

    # ── GPS error count ──
    gps_errors = query_one(cur, """
        SELECT COUNT(*) as cnt
        FROM garmin_daily_metrics
        WHERE total_distance_km > 40
          AND active_calories IS NOT NULL
          AND total_distance_km / NULLIF(active_calories, 0) > 0.04
    """)

    cur.close()
    conn.close()
    print("DB queries complete.\n")

    # ── Build template variables ──
    def get_intensity(name):
        row = intensity.get(name, {})
        return {
            "days": fmt_int(row.get("days", 0)),
            "pct": fmt(row.get("pct", 0)),
            "pct_round": fmt_int(row.get("pct", 0)),
            "acute": fmt_int(row.get("avg_acute", 0)),
            "acute_min": fmt_int(row.get("min_acute", 0)),
            "acute_max": fmt_int(row.get("max_acute", 0)),
        }

    rest = get_intensity("Rest/Recovery")
    light = get_intensity("Light Training")
    mod = get_intensity("Moderate Training")
    hard = get_intensity("Hard Training")
    vhard = get_intensity("Very Hard Training")

    # Combined percentages for Training Philosophy
    rest_days_n = int(intensity.get("Rest/Recovery", {}).get("days", 0))
    light_days_n = int(intensity.get("Light Training", {}).get("days", 0))
    hard_days_n = int(intensity.get("Hard Training", {}).get("days", 0))
    vhard_days_n = int(intensity.get("Very Hard Training", {}).get("days", 0))
    total_activity = int(date_range["activity_days"])
    rest_light_pct = round(100.0 * (rest_days_n + light_days_n) / total_activity) if total_activity else 0
    hard_vhard_pct = round(100.0 * (hard_days_n + vhard_days_n) / total_activity) if total_activity else 0

    # Alert thresholds
    rhr_lo, rhr_hi, rhr_warn, rhr_alert = calculate_thresholds(recovery["rhr_mean"], recovery["rhr_std"])
    hrv_lo, hrv_hi, hrv_warn, hrv_alert = calculate_thresholds_inverted(recovery["hrv_mean"], recovery["hrv_std"])

    sleep_hrs_m = float(sleep["sleep_hrs_mean"]) if sleep["sleep_hrs_mean"] else 0
    sleep_hrs_s = float(sleep["sleep_hrs_std"]) if sleep["sleep_hrs_std"] else 0
    sleep_normal_lo = round(sleep_hrs_m - sleep_hrs_s, 1)
    sleep_normal_hi = round(sleep_hrs_m + sleep_hrs_s, 1)
    sleep_warning = int(round(sleep_hrs_m - 1.5 * sleep_hrs_s))
    sleep_alert = round(sleep_hrs_m - 2 * sleep_hrs_s, 1)

    score_lo, score_hi, score_warn, score_alert = calculate_thresholds_inverted(
        sleep["sleep_score_mean"], sleep["sleep_score_std"])

    # Watch-worn percentage
    total_days = int(date_range["total_days"])
    watch_worn = int(date_range["watch_worn_days"])
    watch_worn_pct = int(round(100.0 * watch_worn / total_days)) if total_days else 0

    # Red flag thresholds
    hrv_red_flag = int(round(float(recovery["hrv_mean"]) - float(recovery["hrv_std"]))) if recovery["hrv_mean"] else "?"
    rhr_red_flag = int(round(float(recovery["rhr_mean"]) + float(recovery["rhr_std"]))) if recovery["rhr_mean"] else "?"
    score_red_flag = 60

    # ── Render profile ──
    profile_vars = {
        "first_date": format_date_short(date_range["first_date"]),
        "last_date": format_date_short(date_range["last_date"]),
        "total_days": fmt_int(date_range["total_days"]),
        "watch_worn_days": fmt_int(date_range["watch_worn_days"]),
        "gps_errors": fmt_int(gps_errors.get("cnt", 0)),
        "rhr_mean": fmt(recovery["rhr_mean"]), "rhr_std": fmt(recovery["rhr_std"]),
        "rhr_min": fmt_int(recovery["rhr_min"]), "rhr_max": fmt_int(recovery["rhr_max"]),
        "hrv_mean": fmt(recovery["hrv_mean"]), "hrv_std": fmt(recovery["hrv_std"]),
        "hrv_min": fmt_int(recovery["hrv_min"]), "hrv_max": fmt_int(recovery["hrv_max"]),
        "hrv_wk_mean": fmt(recovery["hrv_wk_mean"]), "hrv_wk_std": fmt(recovery["hrv_wk_std"]),
        "hrv_wk_min": fmt_int(recovery["hrv_wk_min"]), "hrv_wk_max": fmt_int(recovery["hrv_wk_max"]),
        "vo2_mean": fmt(recovery["vo2_mean"]), "vo2_std": fmt(recovery["vo2_std"]),
        "vo2_min": fmt_int(recovery["vo2_min"]), "vo2_max": fmt_int(recovery["vo2_max_val"]),
        "sleep_hrs_mean": fmt(sleep["sleep_hrs_mean"]), "sleep_hrs_std": fmt(sleep["sleep_hrs_std"]),
        "sleep_hrs_min": fmt_int(sleep["sleep_hrs_min"]), "sleep_hrs_max": fmt_int(sleep["sleep_hrs_max"]),
        "sleep_score_mean": fmt(sleep["sleep_score_mean"]), "sleep_score_std": fmt(sleep["sleep_score_std"]),
        "sleep_score_min": fmt_int(sleep["sleep_score_min"]), "sleep_score_max": fmt_int(sleep["sleep_score_max"]),
        "deep_pct_mean": fmt(sleep["deep_pct_mean"]), "deep_pct_std": fmt(sleep["deep_pct_std"]),
        "deep_pct_min": fmt_int(sleep["deep_pct_min"]), "deep_pct_max": fmt_int(sleep["deep_pct_max"]),
        "rem_pct_mean": fmt(sleep["rem_pct_mean"]), "rem_pct_std": fmt(sleep["rem_pct_std"]),
        "rem_pct_min": fmt_int(sleep["rem_pct_min"]), "rem_pct_max": fmt_int(sleep["rem_pct_max"]),
        "steps_mean": fmt_comma(activity["steps_mean"]), "steps_std": fmt_comma(activity["steps_std"]),
        "steps_min": fmt_comma(activity["steps_min"]), "steps_max": fmt_comma(activity["steps_max"]),
        "dist_mean": fmt(activity["dist_mean"]), "dist_std": fmt(activity["dist_std"]),
        "dist_min": fmt_int(activity["dist_min"]), "dist_max": fmt_int(activity["dist_max"]),
        "acal_mean": fmt_comma(activity["acal_mean"]), "acal_std": fmt_comma(activity["acal_std"]),
        "acal_min": fmt_comma(activity["acal_min"]), "acal_max": fmt_comma(activity["acal_max"]),
        "mod_mins_mean": fmt(activity["mod_mins_mean"]), "mod_mins_std": fmt(activity["mod_mins_std"]),
        "vig_mins_mean": fmt(activity["vig_mins_mean"]), "vig_mins_std": fmt(activity["vig_mins_std"]),
        "rhr_normal_lo": rhr_lo, "rhr_normal_hi": rhr_hi,
        "rhr_warning": rhr_warn, "rhr_alert": rhr_alert,
        "hrv_normal_lo": hrv_lo, "hrv_normal_hi": hrv_hi,
        "hrv_warning": hrv_warn, "hrv_alert": hrv_alert,
        "sleep_normal_lo": sleep_normal_lo, "sleep_normal_hi": sleep_normal_hi,
        "sleep_warning": sleep_warning, "sleep_alert": sleep_alert,
        "score_normal_lo": score_lo, "score_normal_hi": score_hi,
        "score_warning": score_warn, "score_alert": score_alert,
        "hrv_red_flag": hrv_red_flag, "rhr_red_flag": rhr_red_flag,
        "score_red_flag": score_red_flag,
        "watch_worn_pct": watch_worn_pct,
    }

    with open(PROFILE_TEMPLATE, "r") as f:
        profile_content = f.read()
    profile_content = profile_content.format(**profile_vars)
    with open(PROFILE_OUTPUT, "w") as f:
        f.write(profile_content)
    print(f"Updated: {PROFILE_OUTPUT}")

    # ── Render intensity index ──
    intensity_vars = {
        "first_date_long": format_date_long(date_range["first_date"]),
        "last_date_long": format_date_long(date_range["last_date"]),
        "total_days": fmt_int(date_range["total_days"]),
        "activity_days": fmt_int(date_range["activity_days"]),
        "rest_days": rest["days"], "rest_pct": rest["pct"], "rest_pct_round": rest["pct_round"],
        "rest_acute": rest["acute"], "rest_acute_min": rest["acute_min"], "rest_acute_max": rest["acute_max"],
        "light_days": light["days"], "light_pct": light["pct"], "light_pct_round": light["pct_round"],
        "light_acute": light["acute"], "light_acute_min": light["acute_min"], "light_acute_max": light["acute_max"],
        "mod_days": mod["days"], "mod_pct": mod["pct"], "mod_pct_round": mod["pct_round"],
        "mod_acute": mod["acute"], "mod_acute_min": mod["acute_min"], "mod_acute_max": mod["acute_max"],
        "hard_days": hard["days"], "hard_pct": hard["pct"], "hard_pct_round": hard["pct_round"],
        "hard_acute": hard["acute"], "hard_acute_min": hard["acute_min"], "hard_acute_max": hard["acute_max"],
        "vhard_days": vhard["days"], "vhard_pct": vhard["pct"], "vhard_pct_round": vhard["pct_round"],
        "vhard_acute": vhard["acute"], "vhard_acute_min": vhard["acute_min"], "vhard_acute_max": vhard["acute_max"],
        "rest_light_pct": int(rest_light_pct),
        "hard_vhard_pct": int(hard_vhard_pct),
        "p90_cal": fmt_comma(load_thresholds.get("p90_cal")),
    }

    with open(INTENSITY_TEMPLATE, "r") as f:
        intensity_content = f.read()
    intensity_content = intensity_content.format(**intensity_vars)
    with open(INTENSITY_OUTPUT, "w") as f:
        f.write(intensity_content)
    print(f"Updated: {INTENSITY_OUTPUT}")

    print("\nDone. Both YEHWAN files regenerated from templates.")


if __name__ == "__main__":
    main()
